import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timbiriche_flutter/firebase_service.dart';
import 'package:timbiriche_flutter/game_logic.dart';
import 'package:timbiriche_flutter/main.dart';

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('restaura una partida guardada', () {
    final original = TimbiricheGame()..addLine(true, 0, 0);
    final restored = TimbiricheGame()..restoreSnapshot(original.toSnapshot());

    expect(restored.horizontalLines[0][0], isTrue);
    expect(restored.currentPlayer, original.currentPlayer);
    expect(restored.scores, original.scores);
  });

  testWidgets('dibuja correctamente la última caja de la partida', (
    tester,
  ) async {
    final game = TimbiricheGame();
    await tester.pumpWidget(_testApp(game: game));

    for (var row = 0; row < 7; row++) {
      for (var column = 0; column < 6; column++) {
        game.addLine(true, row, column);
      }
    }
    for (var row = 0; row < 6; row++) {
      for (var column = 0; column < 7; column++) {
        game.addLine(false, row, column);
      }
    }
    await tester.pump();

    expect(game.boxes.length, 36);
    expect(tester.takeException(), isNull);
  });

  testWidgets('muestra la experiencia principal', (WidgetTester tester) async {
    await tester.pumpWidget(_testApp());

    expect(find.text('Timbiriche con Tutu'), findsOneWidget);
    expect(find.text('Jugar juntas'), findsOneWidget);
    expect(find.textContaining('juegan por turnos'), findsOneWidget);
    expect(find.text('Nueva partida'), findsOneWidget);
  });

  testWidgets('se adapta a un celular sin desbordamientos', (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(_testApp());
    await tester.pump();

    expect(tester.takeException(), isNull);
    await tester.tap(find.text('Jugar a distancia'));
    await tester.pump();
    expect(find.text('Código de sala'), findsOneWidget);
  });

  testWidgets('se adapta a una tableta Windows horizontal', (tester) async {
    tester.view.physicalSize = const Size(900, 720);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(_testApp());
    await tester.pump();

    expect(tester.takeException(), isNull);
    expect(find.text('Cierra el cuadro'), findsOneWidget);
  });
}

Widget _testApp({TimbiricheGame? game}) => MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (_) => game ?? TimbiricheGame()),
    Provider(create: (_) => FirebaseService()),
  ],
  child: const TimbiricheApp(),
);
