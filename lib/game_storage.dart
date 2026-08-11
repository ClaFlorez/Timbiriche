import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'game_logic.dart';

class SavedGame {
  const SavedGame({required this.game, required this.online});
  final Map<String, dynamic> game;
  final bool online;
}

class GameStorage {
  static const _gameKey = 'saved_timbiriche_game_v2';

  Future<void> save(TimbiricheGame game, {required bool online}) async {
    try {
      final preferences = await SharedPreferences.getInstance();
      await preferences.setString(
        _gameKey,
        jsonEncode({'online': online, 'game': game.toSnapshot()}),
      );
    } catch (error) {
      debugPrint('No se pudo guardar la partida: $error');
    }
  }

  Future<SavedGame?> load() async {
    try {
      final preferences = await SharedPreferences.getInstance();
      final value = preferences.getString(_gameKey);
      if (value == null) return null;
      final decoded = jsonDecode(value) as Map<String, dynamic>;
      return SavedGame(
        online: decoded['online'] == true,
        game: Map<String, dynamic>.from(decoded['game'] as Map),
      );
    } catch (error) {
      debugPrint('No se pudo recuperar la partida: $error');
      return null;
    }
  }

  Future<void> clear() async {
    try {
      final preferences = await SharedPreferences.getInstance();
      await preferences.remove(_gameKey);
    } catch (error) {
      debugPrint('No se pudo borrar la partida guardada: $error');
    }
  }
}
