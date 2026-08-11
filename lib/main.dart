import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:provider/provider.dart';
import 'game_logic.dart';
import 'game_screen.dart';
import 'app_theme.dart';

import 'package:firebase_core/firebase_core.dart';
import 'firebase_service.dart';
import 'firebase_options.dart';

import 'dart:io';
import 'package:window_manager/window_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (!kIsWeb && Platform.isWindows) {
    await windowManager.ensureInitialized();

    const windowSize = Size(900, 720);
    WindowOptions windowOptions = const WindowOptions(
      size: windowSize,
      minimumSize: Size(360, 600),
      center: true,
      backgroundColor: Colors.transparent,
      skipTaskbar: false,
      titleBarStyle: TitleBarStyle.normal,
      title: 'Timbiriche con Tutu',
    );

    windowManager.waitUntilReadyToShow(windowOptions, () async {
      await windowManager.show();
      await windowManager.focus();
      await windowManager.setResizable(true);
    });
  }

  String? initError;
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    debugPrint("Firebase initialized successfully");
  } catch (e) {
    debugPrint("Firebase initialization failed: $e");
    initError = e.toString();
  }

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => TimbiricheGame()),
        Provider(create: (_) => FirebaseService(initError: initError)),
      ],
      child: const TimbiricheApp(),
    ),
  );
}

class TimbiricheApp extends StatelessWidget {
  const TimbiricheApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Timbiriche con Tutu',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const GameScreen(),
    );
  }
}
