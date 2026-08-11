import 'dart:math';
import 'package:flutter/material.dart';

class ButterflyCloud extends StatefulWidget {
  const ButterflyCloud({super.key, this.count = 28});
  final int count;

  @override
  State<ButterflyCloud> createState() => _ButterflyCloudState();
}

class _ButterflyCloudState extends State<ButterflyCloud>
    with TickerProviderStateMixin {
  final _random = Random();
  late final List<_ButterflyMotion> _butterflies;

  @override
  void initState() {
    super.initState();
    _butterflies = List.generate(widget.count, (_) {
      final controller = AnimationController(
        vsync: this,
        duration: Duration(milliseconds: 6500 + _random.nextInt(8500)),
      )..repeat(reverse: _random.nextBool());
      return _ButterflyMotion(
        controller: controller,
        start: Offset(_random.nextDouble(), _random.nextDouble()),
        drift: Offset(
          (_random.nextDouble() - .5) * .28,
          -(.18 + _random.nextDouble() * .42),
        ),
        size: 17 + _random.nextDouble() * 25,
        phase: _random.nextDouble() * pi * 2,
        opacity: .3 + _random.nextDouble() * .5,
      );
    });
  }

  @override
  void dispose() {
    for (final butterfly in _butterflies) {
      butterfly.controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: LayoutBuilder(
        builder: (_, constraints) => Stack(
          children: _butterflies.map((butterfly) {
            return AnimatedBuilder(
              animation: butterfly.controller,
              builder: (_, child) {
                final progress = butterfly.controller.value;
                final wave = sin(progress * pi * 4 + butterfly.phase) * .045;
                final x =
                    (butterfly.start.dx +
                        butterfly.drift.dx * progress +
                        wave) %
                    1;
                final y =
                    (butterfly.start.dy + butterfly.drift.dy * progress) % 1;
                return Positioned(
                  left: x * constraints.maxWidth,
                  top: y * constraints.maxHeight,
                  child: Transform.rotate(
                    angle: sin(progress * pi * 6 + butterfly.phase) * .22,
                    child: Opacity(opacity: butterfly.opacity, child: child),
                  ),
                );
              },
              child: Text('🦋', style: TextStyle(fontSize: butterfly.size)),
            );
          }).toList(),
        ),
      ),
    );
  }
}

class _ButterflyMotion {
  const _ButterflyMotion({
    required this.controller,
    required this.start,
    required this.drift,
    required this.size,
    required this.phase,
    required this.opacity,
  });
  final AnimationController controller;
  final Offset start;
  final Offset drift;
  final double size;
  final double phase;
  final double opacity;
}

class HeroButterfly extends StatefulWidget {
  const HeroButterfly({super.key});

  @override
  State<HeroButterfly> createState() => _HeroButterflyState();
}

class _HeroButterflyState extends State<HeroButterfly>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<Alignment> _route;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 16),
    )..repeat();
    _route = TweenSequence<Alignment>([
      TweenSequenceItem(
        tween: AlignmentTween(
          begin: const Alignment(-1.25, .75),
          end: const Alignment(.65, -.75),
        ).chain(CurveTween(curve: Curves.easeInOutSine)),
        weight: 35,
      ),
      TweenSequenceItem(
        tween: AlignmentTween(
          begin: const Alignment(.65, -.75),
          end: const Alignment(-.55, -.1),
        ).chain(CurveTween(curve: Curves.easeInOutSine)),
        weight: 25,
      ),
      TweenSequenceItem(
        tween: AlignmentTween(
          begin: const Alignment(-.55, -.1),
          end: const Alignment(1.25, .65),
        ).chain(CurveTween(curve: Curves.easeInOutSine)),
        weight: 40,
      ),
    ]).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (_, child) => Align(
          alignment: _route.value,
          child: Transform.rotate(
            angle: sin(_controller.value * pi * 8) * .18,
            child: Transform.scale(
              scaleX: .78 + sin(_controller.value * pi * 20).abs() * .35,
              child: child,
            ),
          ),
        ),
        child: const Text(
          '🦋',
          style: TextStyle(
            fontSize: 48,
            shadows: [
              Shadow(color: Color(0x886E45A8), blurRadius: 12),
              Shadow(color: Colors.white, blurRadius: 4),
            ],
          ),
        ),
      ),
    );
  }
}
