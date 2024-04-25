%%--------------------------------------------------------------------
%% Copyright (C) 2024 hyperimpose.org
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

-module(http_4chan_SUITE).

%% Note: This directive should only be used in test suites.
-export([suite/0, init_per_suite/1, end_per_suite/1, all/0]).
-export([i_4cdn_sfw/0, i_4cdn_sfw/1,
         is2_4chan_sfw/0, is2_4chan_sfw/1,
         i_4cdn_nsfw/0, i_4cdn_nsfw/1,
         is2_4chan_nsfw/0, is2_4chan_nsfw/1]).

-include_lib("common_test/include/ct.hrl").

%%--------------------------------------------------------------------
%% COMMON TEST CALLBACK FUNCTIONS
%%--------------------------------------------------------------------

suite() ->
    [{timetrap, {minutes, 2}}].


init_per_suite(Config) ->
    {ok, _} = application:ensure_all_started(minutia),
    Config.

end_per_suite(_Config) ->
    ok.

%%--------------------------------------------------------------------

all() ->
    [i_4cdn_sfw, is2_4chan_sfw, i_4cdn_nsfw, is2_4chan_nsfw].


%%--------------------------------------------------------------------
%% TEST CASES
%%--------------------------------------------------------------------

i_4cdn_sfw() -> [{timetrap, {seconds, 3}}].

i_4cdn_sfw(_Config) ->
    {ok, R} = minutia:get("https://i.4cdn.org/g/1594686780709.png"),

    #{size := <<"300.06 KB">>,
      filename := <<>>,
      title := <<>>,
      m := http_file_image,
      width := 535,
      t := <<"image/png, 535x420, Size: 300.06 KB">>,
      height := 420,
      explicit := +0.0,
      mimetype := <<"image/png">>,
      artist := <<>>} = R.


is2_4chan_sfw() -> [{timetrap, {seconds, 3}}].

is2_4chan_sfw(_Config) ->
    {ok, R} = minutia:get("https://is2.4chan.org/g/1594686780709.png"),

    #{m := http_file_image,
      t := <<"image/png, 535x420, Size: 300.06 KB">>,
      size := <<"300.06 KB">>,
      filename := <<>>,
      title := <<>>,
      width := 535,
      height := 420,
      explicit := +0.0,
      mimetype := <<"image/png">>,
      artist := <<>>} = R.


i_4cdn_nsfw() -> [{timetrap, {seconds, 3}}].

i_4cdn_nsfw(_Config) ->
    {ok, R} = minutia:get("https://i.4cdn.org/pol/1493993226750.jpg"),

    #{m := http_file_image,
      t := <<"image/jpeg, 1600x1131, Size: 627.27 KB">>,
      size := <<"627.27 KB">>,
      filename := <<>>,
      title := <<>>,
      width := 1600,
      height := 1131,
      explicit := 1.0,
      mimetype := <<"image/jpeg">>,
      artist := <<>>} = R.


is2_4chan_nsfw() -> [{timetrap, {seconds, 3}}].

is2_4chan_nsfw(_Config) ->
    {ok, R} = minutia:get("https://i.4cdn.org/pol/1493993226750.jpg"),

    #{m := http_file_image,
      t := <<"image/jpeg, 1600x1131, Size: 627.27 KB">>,
      size := <<"627.27 KB">>,
      filename := <<>>,
      title := <<>>,
      width := 1600,
      height := 1131,
      explicit := 1.0,
      mimetype := <<"image/jpeg">>,
      artist := <<>>} = R.
