import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app_theme.dart';
import 'game_logic.dart';

class GameGrid extends StatelessWidget {
  const GameGrid({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        const rows = 7;
        const cols = 7;
        final side = constraints.biggest.shortestSide;
        final margin = side * .045;
        final width = constraints.maxWidth - margin * 2;
        final height = constraints.maxHeight - margin * 2;
        final cellWidth = width / (cols - 1);
        final cellHeight = height / (rows - 1);
        final dotSize = side * .032;
        final hitSize = side * .055;

        return Stack(
          clipBehavior: Clip.none,
          children: [
            ..._boxes(context, cellWidth, cellHeight, margin),
            ..._horizontalLines(
              context,
              cellWidth,
              cellHeight,
              hitSize,
              margin,
            ),
            ..._verticalLines(context, cellWidth, cellHeight, hitSize, margin),
            ..._dots(cellWidth, cellHeight, dotSize, margin),
          ],
        );
      },
    );
  }

  List<Widget> _boxes(
    BuildContext context,
    double cw,
    double ch,
    double margin,
  ) {
    final game = context.watch<TimbiricheGame>();
    return game.boxes.entries.map((entry) {
      final parts = entry.key.split('-');
      final row = int.parse(parts[0]);
      final col = int.parse(parts[1]);
      return Positioned(
        left: margin + col * cw + 5,
        top: margin + row * ch + 5,
        width: cw - 10,
        height: ch - 10,
        child: _CapturedBox(player: entry.value),
      );
    }).toList();
  }

  List<Widget> _horizontalLines(
    BuildContext context,
    double cw,
    double ch,
    double hit,
    double margin,
  ) {
    final game = context.watch<TimbiricheGame>();
    return [
      for (var row = 0; row < 7; row++)
        for (var col = 0; col < 6; col++)
          Positioned(
            left: margin + col * cw,
            top: margin + row * ch - hit / 2,
            width: cw,
            height: hit,
            child: _LineTarget(
              filled: game.horizontalLines[row][col],
              horizontal: true,
              onTap: () =>
                  context.read<TimbiricheGame>().addLine(true, row, col),
            ),
          ),
    ];
  }

  List<Widget> _verticalLines(
    BuildContext context,
    double cw,
    double ch,
    double hit,
    double margin,
  ) {
    final game = context.watch<TimbiricheGame>();
    return [
      for (var row = 0; row < 6; row++)
        for (var col = 0; col < 7; col++)
          Positioned(
            left: margin + col * cw - hit / 2,
            top: margin + row * ch,
            width: hit,
            height: ch,
            child: _LineTarget(
              filled: game.verticalLines[row][col],
              horizontal: false,
              onTap: () =>
                  context.read<TimbiricheGame>().addLine(false, row, col),
            ),
          ),
    ];
  }

  List<Widget> _dots(double cw, double ch, double size, double margin) => [
    for (var row = 0; row < 7; row++)
      for (var col = 0; col < 7; col++)
        Positioned(
          left: margin + col * cw - size / 2,
          top: margin + row * ch - size / 2,
          width: size,
          height: size,
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: AppColors.ink,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
              boxShadow: const [
                BoxShadow(color: Color(0x3324163A), blurRadius: 5),
              ],
            ),
          ),
        ),
  ];
}

class _LineTarget extends StatelessWidget {
  const _LineTarget({
    required this.filled,
    required this.horizontal,
    required this.onTap,
  });
  final bool filled;
  final bool horizontal;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: filled ? 'Línea ocupada' : 'Seleccionar línea',
      child: InkWell(
        onTap: filled ? null : onTap,
        borderRadius: BorderRadius.circular(20),
        child: ClipRect(
          child: Center(
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 220),
              width: horizontal ? double.infinity : 5,
              height: horizontal ? 5 : double.infinity,
              margin: horizontal
                  ? const EdgeInsets.symmetric(horizontal: 8)
                  : const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(
                color: filled
                    ? null
                    : AppColors.lavender.withValues(alpha: .78),
                gradient: filled
                    ? const LinearGradient(
                        colors: [Color(0xFF00E5FF), Color(0xFF2979FF)],
                      )
                    : null,
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _CapturedBox extends StatelessWidget {
  const _CapturedBox({required this.player});
  final Player player;

  @override
  Widget build(BuildContext context) {
    final isTutu = player == Player.tutu;
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: .92, end: 1),
      duration: const Duration(milliseconds: 260),
      curve: Curves.easeOut,
      builder: (_, value, child) => Transform.scale(scale: value, child: child),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: isTutu ? AppColors.coralSoft : AppColors.lavender,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Icon(
            isTutu ? Icons.favorite_rounded : Icons.auto_awesome_rounded,
            color: isTutu ? AppColors.coral : AppColors.violet,
          ),
        ),
      ),
    );
  }
}
