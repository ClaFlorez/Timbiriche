import 'package:flutter/material.dart';

enum Player { tutu, abuelita }

class TimbiricheGame extends ChangeNotifier {
  static const _tutuMessages = [
    '¡Weeeyy! Tutu cerró un cuadro precioso.',
    '¡Fantástico, Tutu! Ese cuadro es tuyo.',
    '¡Otra mariposa para Tutu! Sigue jugando.',
    '¡Qué gran jugada, Tutu! Sumaste un punto.',
  ];
  static const _abuelitaMessages = [
    '¡Weeeyy! Un cuadro para ti.',
    '¡Excelente jugada! Ese punto es tuyo.',
    '¡Lo conseguiste! Vuelves a jugar.',
    '¡Qué bonito cuadro! Sumaste un punto.',
  ];

  Player currentPlayer = Player.abuelita;
  Map<Player, int> scores = {Player.tutu: 0, Player.abuelita: 0};

  // 7 rows of 6 horizontal lines (for 6x6 boxes)
  List<List<bool>> horizontalLines = List.generate(
    7,
    (_) => List.filled(6, false),
  );

  // 6 rows of 7 vertical lines (for 6x6 boxes)
  List<List<bool>> verticalLines = List.generate(
    6,
    (_) => List.filled(7, false),
  );

  // Box ownership: row, col -> Player
  Map<String, Player> boxes = {};

  bool animateCapture = false;
  String? lastWinnerMessage;

  bool isGameOver = false;
  Player? winner;

  // Remote play fields
  String? roomId;
  Player? myPlayer; // Player assigned to this device
  bool lastMoveWasLocal = false; // Flag to trigger sync

  Map<String, dynamic> toSnapshot() => {
    'currentPlayer': currentPlayer.name,
    'scores': {
      'tutu': scores[Player.tutu],
      'abuelita': scores[Player.abuelita],
    },
    'horizontalLines': horizontalLines,
    'verticalLines': verticalLines,
    'boxes': boxes.map((key, value) => MapEntry(key, value.name)),
    'isGameOver': isGameOver,
    'winner': winner?.name,
    'lastWinnerMessage': lastWinnerMessage,
    'roomId': roomId,
    'myPlayer': myPlayer?.name,
  };

  void restoreSnapshot(Map<String, dynamic> data) {
    currentPlayer = data['currentPlayer'] == 'tutu'
        ? Player.tutu
        : Player.abuelita;
    final savedScores = data['scores'] as Map?;
    scores = {
      Player.tutu: (savedScores?['tutu'] as num?)?.toInt() ?? 0,
      Player.abuelita: (savedScores?['abuelita'] as num?)?.toInt() ?? 0,
    };
    horizontalLines = _restoreLines(data['horizontalLines'], 7, 6);
    verticalLines = _restoreLines(data['verticalLines'], 6, 7);
    final savedBoxes = data['boxes'] as Map? ?? {};
    boxes = savedBoxes.map(
      (key, value) => MapEntry(
        key.toString(),
        value == 'tutu' ? Player.tutu : Player.abuelita,
      ),
    );
    isGameOver = data['isGameOver'] == true;
    winner = data['winner'] == null
        ? null
        : data['winner'] == 'tutu'
        ? Player.tutu
        : Player.abuelita;
    lastWinnerMessage = data['lastWinnerMessage'] as String?;
    roomId = data['roomId'] as String?;
    myPlayer = data['myPlayer'] == null
        ? null
        : data['myPlayer'] == 'tutu'
        ? Player.tutu
        : Player.abuelita;
    lastMoveWasLocal = false;
    animateCapture = false;
    notifyListeners();
  }

  List<List<bool>> _restoreLines(Object? value, int rows, int columns) {
    if (value is! List || value.length != rows) {
      return List.generate(rows, (_) => List.filled(columns, false));
    }
    return value.map((row) {
      if (row is! List || row.length != columns) {
        return List.filled(columns, false);
      }
      return row.map((cell) => cell == true).toList();
    }).toList();
  }

  void addLine(bool isHorizontal, int r, int c, {bool isRemote = false}) {
    if (isGameOver) return;

    // Check if it's my turn in remote play
    // (If myPlayer is set, we only allow plays for that player, unless it's a remote sync)
    if (!isRemote && myPlayer != null && currentPlayer != myPlayer) return;

    if (!isRemote) {
      lastMoveWasLocal = true;
    } else {
      lastMoveWasLocal = false;
    }

    if (isHorizontal) {
      if (horizontalLines[r][c]) return;
      horizontalLines[r][c] = true;
    } else {
      if (verticalLines[r][c]) return;
      verticalLines[r][c] = true;
    }

    bool formedBox = false;

    // Check all 6x6 possible boxes
    for (int row = 0; row < 6; row++) {
      for (int col = 0; col < 6; col++) {
        String boxKey = '$row-$col';
        if (!boxes.containsKey(boxKey)) {
          // A box requires the top, bottom, left, and right lines
          if (horizontalLines[row][col] &&
              horizontalLines[row + 1][col] &&
              verticalLines[row][col] &&
              verticalLines[row][col + 1]) {
            boxes[boxKey] = currentPlayer;
            scores[currentPlayer] = (scores[currentPlayer] ?? 0) + 1;
            formedBox = true;
            animateCapture = true;

            if (currentPlayer == Player.tutu) {
              lastWinnerMessage =
                  _tutuMessages[scores[Player.tutu]! % _tutuMessages.length];
            } else {
              lastWinnerMessage =
                  _abuelitaMessages[scores[Player.abuelita]! %
                      _abuelitaMessages.length];
            }
          }
        }
      }
    }

    if (boxes.length == 36) {
      isGameOver = true;
      if (scores[Player.tutu]! > scores[Player.abuelita]!) {
        winner = Player.tutu;
        lastWinnerMessage = "¡Tutu gana la partida!";
      } else if (scores[Player.tutu]! < scores[Player.abuelita]!) {
        winner = Player.abuelita;
        lastWinnerMessage = "¡Abuelita gana la partida!";
      } else {
        lastWinnerMessage = "¡Partida empatada! Han jugado de maravilla.";
      }
    } else if (!formedBox) {
      currentPlayer = currentPlayer == Player.tutu
          ? Player.abuelita
          : Player.tutu;
      animateCapture = false;
      lastWinnerMessage = null;
    }

    notifyListeners();
  }

  void syncFromRemote(Map data) {
    currentPlayer = data['currentPlayer'] == 'tutu'
        ? Player.tutu
        : Player.abuelita;

    final remoteScores = data['scores'] as Map?;
    if (remoteScores != null) {
      scores[Player.tutu] = (remoteScores['tutu'] as num?)?.toInt() ?? 0;
      scores[Player.abuelita] =
          (remoteScores['abuelita'] as num?)?.toInt() ?? 0;
    }

    if (data['horizontalLines'] != null) {
      horizontalLines = (data['horizontalLines'] as List).map((row) {
        return (row as List).map((v) => v == true).toList();
      }).toList();
    }

    if (data['verticalLines'] != null) {
      verticalLines = (data['verticalLines'] as List).map((row) {
        return (row as List).map((v) => v == true).toList();
      }).toList();
    }

    Map remoteBoxes = data['boxes'] ?? {};
    boxes = remoteBoxes.map(
      (key, value) => MapEntry(
        key.toString(),
        value == 'tutu' ? Player.tutu : Player.abuelita,
      ),
    );

    isGameOver = data['isGameOver'] ?? false;
    lastMoveWasLocal = false;
    notifyListeners();
  }

  void reset() {
    currentPlayer = Player.abuelita;
    scores = {Player.tutu: 0, Player.abuelita: 0};
    horizontalLines = List.generate(7, (_) => List.filled(6, false));
    verticalLines = List.generate(6, (_) => List.filled(7, false));
    boxes.clear();
    animateCapture = false;
    lastWinnerMessage = null;
    isGameOver = false;
    winner = null;
    lastMoveWasLocal = false;
    notifyListeners();
  }

  void clearRoomState() {
    roomId = null;
    myPlayer = null;
    reset();
  }
}
