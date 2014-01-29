$(function() {

  var template_url = 'icon-map.json';
  var map_window_options = {width: 400, height: 400};
  var ssd_window_options = {width: 95, height: 160};
  var games_window_options = {width: 200};
  var game_window_options = {width: 200};

  $('#show-map').on('click', function(e) {
    e.preventDefault();
    SFB.Application.load('g/5b3e2e8e3ed44a84ac89bad2d7c3be94/map', function(map) {
      SFB.Application.showMap(map, template_url, map_window_options);
    });
  });

  $('#show-ssd').on('click', function(e) {
    e.preventDefault();
    SFB.Application.load('g/5b3e2e8e3ed44a84ac89bad2d7c3be94/unit/9c3f982d07cb4e469ab01e5dc466f09f', function(ssd) {
      SFB.Application.showSSD(ssd, template_url, ssd_window_options);
    });
  });

  $('#show-games').on('click', function(e) {
    e.preventDefault();
    SFB.Application.load('g', function(games) {
      SFB.Application.showGames(games, games_window_options);
    });
  });

  $('#show-game').on('click', function(e) {
    e.preventDefault();
    SFB.Application.load('g/5b3e2e8e3ed44a84ac89bad2d7c3be94', function(game) {
      SFB.Application.showGame(game, game_window_options);
    });
  });
});
