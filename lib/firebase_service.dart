import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:http/http.dart' as http;
import 'game_logic.dart';
import 'firebase_options.dart';

class FirebaseService {
  final String? initError;
  FirebaseService({this.initError});

  Stream<bool> get connectionStatus {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.windows) {
      return FirebaseDatabase.instance.ref('.info/connected').onValue.map((
        event,
      ) {
        return event.snapshot.value as bool? ?? false;
      });
    } else {
      // Windows REST fallback for connection status
      return Stream.periodic(const Duration(seconds: 5), (_) async {
        try {
          final url = "${DefaultFirebaseOptions.android.databaseURL}/.json";
          final res = await http
              .get(Uri.parse(url))
              .timeout(const Duration(seconds: 3));
          return res.statusCode == 200;
        } catch (_) {
          return false;
        }
      }).asyncMap((b) => b);
    }
  }

  String get _baseUrl => DefaultFirebaseOptions.android.databaseURL ?? "";

  DatabaseReference? get _dbRef {
    try {
      return FirebaseDatabase.instance.ref('rooms');
    } catch (e) {
      return null;
    }
  }

  Future<void> createRoom(String rid, TimbiricheGame game) async {
    game.roomId = rid;
    game.myPlayer = Player.abuelita;
    debugPrint("Firebase: Creating room $rid as Abuelita");

    final data = {
      'currentPlayer': 'abuelita',
      'scores': {'tutu': 0, 'abuelita': 0},
      'horizontalLines': List.generate(7, (_) => List.filled(6, false)),
      'verticalLines': List.generate(6, (_) => List.filled(7, false)),
      'boxes': {},
      'isGameOver': false,
    };

    if (kIsWeb || defaultTargetPlatform != TargetPlatform.windows) {
      final ref = _dbRef;
      if (ref == null) return;
      await ref.child(rid).set(data);
    } else {
      final url = "$_baseUrl/rooms/$rid.json";
      await http.put(Uri.parse(url), body: jsonEncode(data));
    }
  }

  Future<void> joinRoom(String rid, TimbiricheGame game) async {
    game.roomId = rid;
    game.myPlayer = Player.tutu;
    debugPrint("Firebase: Joining room $rid as Tutu");
    // Listener will sync the state
  }

  void syncMove(String rid, TimbiricheGame game) {
    if (game.roomId == null) return;

    final data = {
      'currentPlayer': game.currentPlayer == Player.tutu ? 'tutu' : 'abuelita',
      'scores': {
        'tutu': game.scores[Player.tutu],
        'abuelita': game.scores[Player.abuelita],
      },
      'horizontalLines': game.horizontalLines,
      'verticalLines': game.verticalLines,
      'boxes': game.boxes.map(
        (key, value) =>
            MapEntry(key, value == Player.tutu ? 'tutu' : 'abuelita'),
      ),
      'isGameOver': game.isGameOver,
    };

    if (kIsWeb || defaultTargetPlatform != TargetPlatform.windows) {
      final ref = _dbRef;
      if (ref == null) return;
      debugPrint("Firebase: Syncing move to room ${game.roomId!}");
      ref.child(game.roomId!).update(data);
    } else {
      final url = "$_baseUrl/rooms/${game.roomId!}.json";
      http.patch(Uri.parse(url), body: jsonEncode(data));
    }
  }

  StreamSubscription? _windowsSub;

  void listenToRoom(String rid, TimbiricheGame game) {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.windows) {
      final ref = _dbRef;
      if (ref == null) return;

      ref.child(rid).onValue.listen((event) {
        final data = event.snapshot.value as Map?;
        if (data == null) {
          debugPrint("Firebase: No data found for room $rid");
          return;
        }

        debugPrint("Firebase: Received update for room $rid");
        game.syncFromRemote(data);
      });
    } else {
      // Windows REST Fallback with long polling or SSE
      _windowsSub?.cancel();
      _startSseListener(rid, game);
    }
  }

  void _startSseListener(String rid, TimbiricheGame game) async {
    final client = http.Client();
    final url = "$_baseUrl/rooms/$rid.json";
    final request = http.Request("GET", Uri.parse(url));
    request.headers["Accept"] = "text/event-stream";

    try {
      final response = await client.send(request);
      _windowsSub = response.stream
          .transform(utf8.decoder)
          .transform(const LineSplitter())
          .listen((line) {
            if (line.startsWith("data: ")) {
              final jsonStr = line.substring(6);
              if (jsonStr == "null") return;
              try {
                final decoded = jsonDecode(jsonStr);
                if (decoded is Map && decoded.containsKey('data')) {
                  // SSE format for patch/put often has a 'data' field
                  final actualData = decoded['data'];
                  if (actualData is Map) {
                    // This is complex because REST SSE sends patches.
                    // For simplicity, we can just fetch the whole state when any event happens
                    _fetchRoomSnapshot(rid, game);
                  }
                } else if (decoded == null) {
                  // ignore
                } else {
                  _fetchRoomSnapshot(rid, game);
                }
              } catch (e) {
                debugPrint("Firebase SSE Parse Error: $e");
              }
            }
          });
    } catch (e) {
      debugPrint("Firebase Windows SSE Error: $e");
    }
  }

  void _fetchRoomSnapshot(String rid, TimbiricheGame game) async {
    try {
      final url = "$_baseUrl/rooms/$rid.json";
      final res = await http.get(Uri.parse(url));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        if (data is Map) {
          game.syncFromRemote(data);
        }
      }
    } catch (e) {
      debugPrint("Firebase Fetch Error: $e");
    }
  }
}
