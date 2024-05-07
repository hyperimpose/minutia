%%--------------------------------------------------------------------
%% Copyright (C) 2023-2024 hyperimpose.org
%%
%% This file is part of minutia.
%%
%% This program is free software: you can redistribute it and/or modify
%% it under the terms of the GNU Affero General Public License as published
%% by the Free Software Foundation, version 3.
%%
%% This program is distributed in the hope that it will be useful,
%% but WITHOUT ANY WARRANTY; without even the implied warranty of
%% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%% GNU Affero General Public License for more details.
%%
%% You should have received a copy of the GNU Affero General Public License
%% along with this program.  If not, see <https://www.gnu.org/licenses/>.
%%--------------------------------------------------------------------

-module(minutia).

-behaviour(gen_server).


-include_lib("kernel/include/logger.hrl").


%% API
-export([start_link/0, get/1, get/2, set_http_useragent/1,
         set_language/1, set_max_filesize/1, set_max_htmlsize/1,
         reload_port/0]).

-export_types([options/1, response/1]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2,
         terminate/2, code_change/3, format_status/2]).


%% Macros
-define(NAME, ?MODULE).
-define(LK(Link, Lang), {Link, Lang}).

%% Gen Server state
-record(link, {key, froms=[]}).
-record(state, {port, worker}).

%% Types
-type options() :: #{lang => binary(),
                     timeout => integer(),
                     skip_cache => boolean()}.

-type response() :: {ok, minutia_response:http()}
                  | false
                  | {error, Message :: binary()}.


%%%===================================================================
%%% API
%%%===================================================================

%%--------------------------------------------------------------------
%% @private
%% Meant to be called by the application supervisor.
%%--------------------------------------------------------------------

-spec start_link() ->
          {ok, Pid :: pid()} |
          {error, Error :: {already_started, pid()}} |
          {error, Error :: term()} |
          ignore.

start_link() ->
    gen_server:start_link({local, ?NAME}, ?MODULE, [], []).


%%--------------------------------------------------------------------
%% @equiv get(Link, #{})
%% @end
%%--------------------------------------------------------------------

-spec get(Link :: string()) ->
          response() | {error, unsupported_scheme}.

get(Link) ->
    get(Link, #{lang => <<"en">>}).


%%--------------------------------------------------------------------

-spec get(Link :: string(), Options :: options()) ->
          response() | {error, unsupported_scheme}.

get(LinkAny, Opts) ->
    Link = unicode:characters_to_binary(LinkAny),
    Lang = iolist_to_binary(maps:get(lang, Opts, <<"en">>)),
    Timeout = maps:get(timeout, Opts, 15_000),  % 15 seconds default

    case maps:get(skip_cache, Opts, false) of
        true  -> get_live(Link, Lang, Timeout);
        false -> get_with_cache(Link, Lang, Timeout)
    end.

get_with_cache(Link, Lang, Timeout) ->
    Cache = persistent_term:get({?MODULE, cache}),
    case polycache:get(Cache, ?LK(Link, Lang)) of
        {ok, Hit} -> Hit;
        _Miss     -> get_live(Link, Lang, Timeout)
    end.

get_live(Link, Lang, Timeout) ->
    case scheme(Link) of
        <<"http">>  -> gen_server:call(?NAME, {http_get, Link, Lang}, Timeout);
        <<"https">> -> gen_server:call(?NAME, {http_get, Link, Lang}, Timeout);
        _Else       -> {error, unsupported_scheme}
    end.

%%--------------------------------------------------------------------

set_http_useragent(UA) -> gen_server:call(?NAME, {set_http_useragent, UA}).
set_language(Lang)     -> gen_server:call(?NAME, {set_language, Lang}).
set_max_filesize(Size) -> gen_server:call(?NAME, {set_max_filesize, Size}).
set_max_htmlsize(Size) -> gen_server:call(?NAME, {set_max_htmlsize, Size}).

%%--------------------------------------------------------------------

reload_port() ->
    gen_server:call(?NAME, reload_port).


%%%===================================================================
%%% gen_server callbacks
%%%===================================================================

-spec init(term()) -> {ok, State :: #state{}}.

init([]) ->
    process_flag(trap_exit, true),

    Port = load_port(),

    {ok, Cache} = polycache:new(1_000_000),
    ok = persistent_term:put({?MODULE, cache}, Cache),

    Worker = ets:new(minutia_worker, [set, private, {keypos, 2}]),

    {ok, #state{port = Port, worker = Worker}}.

%%--------------------------------------------------------------------

handle_call({http_get, Link, Lang}, From, State) ->
    http_get(Link, Lang, From, State);

handle_call({set_http_useragent, UA}, _From, #state{port = Port} = State) ->
    set_http_useragent(Port, UA),
    {reply, ok, State};
handle_call({set_language, Lang}, _From, #state{port = Port} = State)         ->
    set_language(Port, Lang),
    {reply, ok, State};
handle_call({set_max_filesize, Size}, _From, #state{port = Port} = State) ->
    set_max_filesize(Port, Size),
    {reply, ok, State};
handle_call({set_max_htmlsize, Size}, _From, #state{port = Port} = State) ->
    set_max_htmlsize(Port, Size),
    {reply, ok, State};

handle_call(reload_port, _From, State) ->
    {ok, State1} = reload_port(State),
    {reply, ok, State1};

handle_call(stop, _From, #state{port = Port} = State) ->
    Port ! {self(), close},
    {stop, normal, State};

handle_call(_Request, _From, State) ->
    Reply = ok,
    {reply, Reply, State}.

%%--------------------------------------------------------------------

handle_cast(_Request, State) ->
    {noreply, State}.

%%--------------------------------------------------------------------

-spec handle_info(Info :: timeout() | term(), State :: term()) ->
          {noreply, NewState :: term()} |
          {noreply, NewState :: term(), Timeout :: timeout()} |
          {noreply, NewState :: term(), hibernate} |
          {stop, Reason :: normal | term(), NewState :: term()}.
handle_info({Port, {data, Data}}, #state{port = Port} = State) ->
    port_in_dispatcher(Data, State);
handle_info({'EXIT', Port, PosixCode}, #state{port = Port} = State) ->
    {stop, {port_terminated, Port, PosixCode}, State};
handle_info(_Info, State) ->
    {noreply, State}.

%%--------------------------------------------------------------------

-spec terminate(Reason :: normal | shutdown | {shutdown, term()} | term(),
                State :: term()) -> any().

terminate(_Reason, #state{port = Port}) ->
    Port ! {self(), close},
    ok.

%%--------------------------------------------------------------------

-spec code_change(OldVsn :: term() | {down, term()},
                  State :: term(),
                  Extra :: term()) -> {ok, NewState :: term()} |
          {error, Reason :: term()}.

code_change(_OldVsn, State, _Extra) ->
    {ok, State1} = reload_port(State),
    {ok, State1}.

%%--------------------------------------------------------------------

-spec format_status(Opt :: normal | terminate,
                    Status :: list()) -> Status :: term().

format_status(_Opt, Status) ->
    Status.


%%%===================================================================
%%% Internal functions
%%%===================================================================

load_port() ->
    Command = ["python3 ", code:priv_dir(minutia), "/bin/libminutia"],
    Port = open_port({spawn, Command}, [{packet, 2}]),

    {ok, HttpUseragent} = application:get_env(minutia, http_useragent),
    {ok, Language} = application:get_env(minutia, language),
    {ok, MaxFilesize} = application:get_env(minutia, max_filesize),
    {ok, MaxHtmlsize} = application:get_env(minutia, max_htmlsize),
    set_http_useragent(Port, HttpUseragent),
    set_language(Port, Language),
    set_max_filesize(Port, MaxFilesize),
    set_max_htmlsize(Port, MaxHtmlsize),

    Port.


reload_port(#state{port = Port} = State) ->
    Port ! {self(), close},
    {ok, State#state{port = load_port()}}.


%%% Outgoing port handlers ===========================================

http_get(Link, Lang, From, State) ->
    #state{port = Port, worker = Worker} = State,

    case ets:lookup(Worker, ?LK(Link, Lang)) of
        [#link{froms=Froms} = L] ->
            ets:insert(Worker, L#link{froms=[From | Froms]});
        []                       ->
            ets:insert(Worker, #link{key=?LK(Link, Lang), froms=[From]}),
            Port ! {self(), {command, [1, Link, 0, Lang]}}
    end,
    {noreply, State}.


set_http_useragent(Port, UA) ->
    Port ! {self(), {command, [255, UA]}}.


set_language(Port, Lang) ->
    Port ! {self(), {command, [254, Lang]}}.


set_max_filesize(Port, Size) ->
    Port ! {self(), {command, [253, integer_to_binary(Size)]}}.


set_max_htmlsize(Port, Size) ->
    Port ! {self(), {command, [252, integer_to_binary(Size)]}}.


%%% Incoming port handlers ===========================================

port_in_dispatcher(Data, State) ->
    case bencode:decode(Data) of
        [<<"http">>, Payload]       -> http_got(Payload, State);
        [<<"log">>, Level, Message] -> log_got(Level, Message, State);
        Else                        ->
            ?LOG_ERROR("Undefined response: ~p", [Else]),
            {noreply, State}
    end.


http_got(Payload, #state{worker = Worker} = State) ->
    #{<<"_link">> := Link, <<"_lang">> := Lang} = Payload,
    Response = minutia_response:http(Payload),

    [#link{froms = Froms}] = ets:lookup(Worker, ?LK(Link, Lang)),
    [gen_server:reply(From, Response) || From <- Froms],
    ets:delete(Worker, ?LK(Link, Lang)),

    Cache = persistent_term:get({?MODULE, cache}),
    Ttl = case Payload of
              #{<<"_ttl">> := Ttl1} when Ttl1 >= 0 ->
                  Ttl1;
              _Else                                ->
                  erlang:system_time(seconds) + 300  % 5 minute forced cache
          end,
    polycache:set(Cache, ?LK(Link, Lang), Response, #{ttl => Ttl}),

    {noreply, State}.


log_got(Level, Message, State) ->
    case Level of
        <<"debug">>     -> ?LOG_DEBUG(Message);
        <<"info">>      -> ?LOG_INFO(Message);
        <<"notice">>    -> ?LOG_NOTICE(Message);
        <<"error">>     -> ?LOG_ERROR(Message);
        <<"emergency">> -> ?LOG_EMERGENCY(Message);
        <<"warning">>   -> ?LOG_WARNING(Message);
        Else -> ?LOG_ERROR("[??? log level: ~p]: ~p", [Else, Message])
    end,
    {noreply, State}.


%%%===================================================================
%%% Helpers
%%%===================================================================

-define(LC(C), C >= $a andalso C =< $z).
-define(UC(C), C >= $A andalso C =< $Z).
-define(ALPHA(C), ?UC(C) orelse ?LC(C)).
-define(DIGIT(C), C >= $0 andalso C =< $9).

scheme(Link) ->
    string:lowercase(scheme(Link, <<>>)).

scheme(<<C/utf8, R/binary>>,  Acc) when ?ALPHA(C) -> scheme1(R, <<Acc/binary, C/utf8>>);
scheme(_Else, _Acc)                -> <<>>.  % Invalid Link

scheme1(<<C/utf8,  R/binary>>, Acc) when ?ALPHA(C) -> scheme1(R, <<Acc/binary, C/utf8>>);
scheme1(<<C/utf8,  R/binary>>, Acc) when ?DIGIT(C) -> scheme1(R, <<Acc/binary, C/utf8>>);
scheme1(<<$+, R/binary>>, Acc)                -> scheme1(R, <<Acc/binary, $+>>);
scheme1(<<$-, R/binary>>, Acc)                -> scheme1(R, <<Acc/binary, $->>);
scheme1(<<$., R/binary>>, Acc)                -> scheme1(R, <<Acc/binary, $.>>);
scheme1(<<$:, _/binary>>, Acc)                -> Acc;
scheme1(_Else,           _Acc)                -> <<>>.  % Invalid link
