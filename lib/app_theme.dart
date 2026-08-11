import 'package:flutter/material.dart';

abstract final class AppColors {
  static const ink = Color(0xFF24163A);
  static const muted = Color(0xFF756B82);
  static const surface = Color(0xFFFFFBF7);
  static const canvas = Color(0xFFF6F1F8);
  static const violet = Color(0xFF6E45A8);
  static const violetDark = Color(0xFF4A2B76);
  static const lavender = Color(0xFFE9DDF4);
  static const coral = Color(0xFFEF746C);
  static const coralSoft = Color(0xFFFFE1DC);
  static const success = Color(0xFF2D8067);
}

ThemeData buildAppTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: AppColors.violet,
    brightness: Brightness.light,
    primary: AppColors.violet,
    secondary: AppColors.coral,
    surface: AppColors.surface,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: AppColors.canvas,
    fontFamily: 'Segoe UI',
    textTheme: const TextTheme(
      headlineSmall: TextStyle(
        color: AppColors.ink,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.5,
      ),
      titleMedium: TextStyle(color: AppColors.ink, fontWeight: FontWeight.w700),
      bodyMedium: TextStyle(color: AppColors.muted, height: 1.35),
      labelLarge: TextStyle(fontWeight: FontWeight.w700, letterSpacing: 0.1),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      hintStyle: const TextStyle(color: AppColors.muted),
      prefixIconColor: AppColors.violet,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: AppColors.lavender),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: AppColors.violet, width: 1.5),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
    ),
  );
}
