import 'dart:math';
import 'package:audioplayers/audioplayers.dart';
import 'package:confetti/confetti.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app_theme.dart';
import 'firebase_service.dart';
import 'game_grid.dart';
import 'game_logic.dart';
import 'game_storage.dart';
import 'magic_effects.dart';

enum PlayMode { local, online }

class GameScreen extends StatefulWidget {
  const GameScreen({super.key});

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  late final ConfettiController _captureConfetti;
  late final ConfettiController _winnerConfetti;
  late final AudioPlayer _audioPlayer;
  late final AudioPlayer _effectPlayer;
  final _roomController = TextEditingController();
  final _storage = GameStorage();
  TimbiricheGame? _game;
  bool _isConnecting = false;
  bool _musicEnabled = true;
  int _capturedBoxes = 0;
  PlayMode _playMode = PlayMode.local;
  bool _restoreStarted = false;
  bool _restoring = false;

  @override
  void initState() {
    super.initState();
    _captureConfetti = ConfettiController(duration: const Duration(seconds: 1));
    _winnerConfetti = ConfettiController(duration: const Duration(seconds: 5));
    _audioPlayer = AudioPlayer()..setReleaseMode(ReleaseMode.loop);
    _effectPlayer = AudioPlayer();
    _playMusic();
  }

  Future<void> _playMusic() async {
    try {
      await _audioPlayer.play(AssetSource('audio/joyful_bgm.mp3'), volume: .2);
    } catch (error) {
      debugPrint('No se pudo iniciar la música: $error');
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final game = context.read<TimbiricheGame>();
    if (_game != game) {
      _game?.removeListener(_onGameChanged);
      _game = game..addListener(_onGameChanged);
      if (!_restoreStarted) {
        _restoreStarted = true;
        _restoreSavedGame(game);
      }
    }
  }

  Future<void> _restoreSavedGame(TimbiricheGame game) async {
    _restoring = true;
    final saved = await _storage.load();
    if (!mounted) return;
    if (saved != null) {
      game.restoreSnapshot(saved.game);
      _capturedBoxes = game.boxes.length;
      setState(() {
        _playMode = saved.online ? PlayMode.online : PlayMode.local;
        _roomController.text = game.roomId ?? '';
      });
      if (saved.online && game.roomId != null) {
        context.read<FirebaseService>().listenToRoom(game.roomId!, game);
        _showMessage('Partida recuperada. Puedes continuar donde la dejaste.');
      }
    }
    _restoring = false;
  }

  void _onGameChanged() {
    final game = _game;
    if (game == null) return;
    if (!_restoring) {
      _storage.save(game, online: _playMode == PlayMode.online);
    }
    if (game.boxes.length > _capturedBoxes) {
      _capturedBoxes = game.boxes.length;
      _captureConfetti.play();
      _playCaptureSound();
    } else if (game.boxes.isEmpty) {
      _capturedBoxes = 0;
    }
    if (game.isGameOver) {
      _winnerConfetti.play();
    } else {
      _winnerConfetti.stop();
    }
    if (game.roomId != null && game.lastMoveWasLocal) {
      context.read<FirebaseService>().syncMove(game.roomId!, game);
    }
  }

  Future<void> _playCaptureSound() async {
    try {
      await _effectPlayer.stop();
      await _effectPlayer.play(
        AssetSource('audio/cuadro_brillante.mp3'),
        volume: .9,
      );
    } catch (error) {
      debugPrint('No se pudo reproducir el efecto: $error');
    }
  }

  @override
  void dispose() {
    _game?.removeListener(_onGameChanged);
    _captureConfetti.dispose();
    _winnerConfetti.dispose();
    _audioPlayer.dispose();
    _effectPlayer.dispose();
    _roomController.dispose();
    super.dispose();
  }

  Future<void> _toggleMusic() async {
    setState(() => _musicEnabled = !_musicEnabled);
    if (_musicEnabled) {
      await _playMusic();
    } else {
      await _audioPlayer.pause();
    }
  }

  Future<void> _selectMode(PlayMode mode) async {
    if (_playMode == mode) return;
    final game = context.read<TimbiricheGame>();
    game.clearRoomState();
    setState(() {
      _playMode = mode;
      _roomController.clear();
      _capturedBoxes = 0;
    });
    await _storage.save(game, online: mode == PlayMode.online);
  }

  Future<void> _connect({required bool create}) async {
    final roomId = _roomController.text.trim().toUpperCase();
    if (roomId.isEmpty) {
      _showMessage('Escribe un código para la sala.');
      return;
    }

    setState(() => _isConnecting = true);
    final game = context.read<TimbiricheGame>();
    final service = context.read<FirebaseService>();
    try {
      game.clearRoomState();
      if (create) {
        await service.createRoom(roomId, game);
      } else {
        await service.joinRoom(roomId, game);
      }
      service.listenToRoom(roomId, game);
      await _storage.save(game, online: true);
      if (mounted) {
        _showMessage(
          create
              ? 'Sala creada. Abuelita comienza la partida.'
              : 'Te has unido a la sala como Tutu.',
        );
      }
    } catch (error) {
      if (mounted) {
        _showMessage('No se pudo conectar con la sala. Inténtalo de nuevo.');
      }
      debugPrint('Error de conexión: $error');
    } finally {
      if (mounted) setState(() => _isConnecting = false);
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          const Positioned.fill(child: _AmbientBackground()),
          const Positioned.fill(child: ButterflyCloud(count: 34)),
          const Positioned.fill(child: HeroButterfly()),
          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 980),
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 14),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final tabletLayout = constraints.maxWidth >= 720;
                      final header = _Header(
                        musicEnabled: _musicEnabled,
                        onMusicPressed: _toggleMusic,
                      );
                      final connection = _ConnectionPanel(
                        controller: _roomController,
                        isConnecting: _isConnecting,
                        playMode: _playMode,
                        onCreate: () => _connect(create: true),
                        onJoin: () => _connect(create: false),
                      );
                      final modeSelector = _ModeSelector(
                        selected: _playMode,
                        onSelected: _selectMode,
                      );

                      if (tabletLayout) {
                        return Column(
                          children: [
                            header,
                            const SizedBox(height: 10),
                            modeSelector,
                            const SizedBox(height: 12),
                            connection,
                            const SizedBox(height: 12),
                            const Expanded(
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  Expanded(flex: 5, child: _BoardCard()),
                                  SizedBox(width: 14),
                                  SizedBox(
                                    width: 300,
                                    child: Column(
                                      children: [
                                        _GameStatus(),
                                        SizedBox(height: 12),
                                        Expanded(child: _GameGuideCard()),
                                        SizedBox(height: 12),
                                        _FooterActions(vertical: true),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        );
                      }

                      return Column(
                        children: [
                          header,
                          const SizedBox(height: 8),
                          modeSelector,
                          const SizedBox(height: 10),
                          connection,
                          const SizedBox(height: 10),
                          const _GameStatus(),
                          const SizedBox(height: 10),
                          const Expanded(child: _BoardCard()),
                          const SizedBox(height: 10),
                          const _FooterActions(),
                        ],
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
          Align(
            alignment: Alignment.center,
            child: ConfettiWidget(
              confettiController: _captureConfetti,
              blastDirectionality: BlastDirectionality.explosive,
              emissionFrequency: .12,
              numberOfParticles: 28,
              minBlastForce: 9,
              maxBlastForce: 19,
              gravity: .13,
              createParticlePath: _captureParticlePath,
              colors: const [
                AppColors.violet,
                AppColors.coral,
                Color(0xFFF2C66D),
                Color(0xFFFF69CF),
                Colors.white,
              ],
            ),
          ),
          Align(
            alignment: Alignment.topCenter,
            child: ConfettiWidget(
              confettiController: _winnerConfetti,
              blastDirection: pi / 2,
              blastDirectionality: BlastDirectionality.directional,
              shouldLoop: true,
              emissionFrequency: .22,
              numberOfParticles: 18,
              gravity: .035,
              minBlastForce: 4,
              maxBlastForce: 11,
              createParticlePath: _balloonPath,
              colors: const [
                Color(0xFFFF4F72),
                Color(0xFFFFC928),
                Color(0xFF34C8FF),
                Color(0xFF7F5AF0),
                Color(0xFF35D07F),
                Color(0xFFFF8A3D),
                Color(0xFFFF69CF),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

Path _balloonPath(Size size) {
  final path = Path();
  final width = size.width * 1.45;
  final height = size.height * 1.65;
  path.moveTo(width * .5, height * .78);
  path.cubicTo(-width * .05, height * .52, width * .08, 0, width * .5, 0);
  path.cubicTo(
    width * .92,
    0,
    width * 1.05,
    height * .52,
    width * .5,
    height * .78,
  );
  path.lineTo(width * .62, height * .9);
  path.lineTo(width * .38, height * .9);
  path.close();
  return path;
}

Path _captureParticlePath(Size size) {
  return Path()..addOval(Rect.fromLTWH(0, 0, size.width, size.height));
}

class _AmbientBackground extends StatelessWidget {
  const _AmbientBackground();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF8F3FA), Color(0xFFFFF4EF)],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: -80,
            right: -70,
            child: _Glow(color: AppColors.coralSoft, size: 230),
          ),
          Positioned(
            bottom: -100,
            left: -80,
            child: _Glow(color: AppColors.lavender, size: 280),
          ),
        ],
      ),
    );
  }
}

class _Glow extends StatelessWidget {
  const _Glow({required this.color, required this.size});
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: color.withValues(alpha: .72),
      shape: BoxShape.circle,
    ),
  );
}

class _Header extends StatelessWidget {
  const _Header({required this.musicEnabled, required this.onMusicPressed});
  final bool musicEnabled;
  final VoidCallback onMusicPressed;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [AppColors.violet, AppColors.violetDark],
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Image.asset(
              'assets/images/app_icon_v2.png',
              fit: BoxFit.cover,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Timbiriche con Tutu',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Text('Una partida para compartir en familia'),
            ],
          ),
        ),
        IconButton.filledTonal(
          tooltip: musicEnabled ? 'Silenciar música' : 'Activar música',
          onPressed: onMusicPressed,
          icon: Icon(
            musicEnabled ? Icons.volume_up_rounded : Icons.volume_off_rounded,
          ),
        ),
      ],
    );
  }
}

class _ConnectionPanel extends StatelessWidget {
  const _ConnectionPanel({
    required this.controller,
    required this.isConnecting,
    required this.playMode,
    required this.onCreate,
    required this.onJoin,
  });
  final TextEditingController controller;
  final bool isConnecting;
  final PlayMode playMode;
  final VoidCallback onCreate;
  final VoidCallback onJoin;

  @override
  Widget build(BuildContext context) {
    return Consumer<TimbiricheGame>(
      builder: (context, game, _) {
        if (playMode == PlayMode.local) {
          return const _Surface(
            padding: EdgeInsets.symmetric(horizontal: 14, vertical: 11),
            child: Row(
              children: [
                Icon(Icons.people_alt_rounded, color: AppColors.violet),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Tú y Tutu juegan por turnos en este dispositivo. La partida se guarda automáticamente.',
                    style: TextStyle(
                      color: AppColors.ink,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                ),
                Icon(Icons.cloud_done_rounded, color: AppColors.success),
              ],
            ),
          );
        }
        if (game.roomId != null) {
          return _Surface(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            child: Row(
              children: [
                const Icon(Icons.link_rounded, color: AppColors.success),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Sala ${game.roomId} · Juegas como ${game.myPlayer == Player.tutu ? 'Tutu' : 'Abuelita'}',
                    style: Theme.of(
                      context,
                    ).textTheme.titleMedium?.copyWith(fontSize: 14),
                  ),
                ),
                const _ConnectionBadge(),
              ],
            ),
          );
        }

        return _Surface(
          padding: const EdgeInsets.all(12),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 470;
              final field = TextField(
                controller: controller,
                textCapitalization: TextCapitalization.characters,
                decoration: const InputDecoration(
                  hintText: 'Código de sala',
                  prefixIcon: Icon(Icons.key_rounded),
                  isDense: true,
                ),
              );
              final buttons = Row(
                children: [
                  Expanded(
                    child: FilledButton(
                      onPressed: isConnecting ? null : onCreate,
                      child: const Text('Crear'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: isConnecting ? null : onJoin,
                      child: isConnecting
                          ? const SizedBox.square(
                              dimension: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Unirse'),
                    ),
                  ),
                ],
              );

              if (narrow) {
                return Column(
                  children: [field, const SizedBox(height: 8), buttons],
                );
              }
              return Row(
                children: [
                  Expanded(flex: 3, child: field),
                  const SizedBox(width: 10),
                  Expanded(flex: 2, child: buttons),
                ],
              );
            },
          ),
        );
      },
    );
  }
}

class _ModeSelector extends StatelessWidget {
  const _ModeSelector({required this.selected, required this.onSelected});
  final PlayMode selected;
  final ValueChanged<PlayMode> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: SegmentedButton<PlayMode>(
        segments: const [
          ButtonSegment(
            value: PlayMode.local,
            icon: Icon(Icons.people_alt_rounded),
            label: Text('Jugar juntas'),
          ),
          ButtonSegment(
            value: PlayMode.online,
            icon: Icon(Icons.language_rounded),
            label: Text('Jugar a distancia'),
          ),
        ],
        selected: {selected},
        onSelectionChanged: (selection) => onSelected(selection.first),
        showSelectedIcon: false,
        style: ButtonStyle(
          visualDensity: VisualDensity.compact,
          shape: WidgetStatePropertyAll(
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
      ),
    );
  }
}

class _ConnectionBadge extends StatelessWidget {
  const _ConnectionBadge();

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<bool>(
      stream: context.read<FirebaseService>().connectionStatus,
      builder: (_, snapshot) {
        final online = snapshot.data ?? false;
        return Tooltip(
          message: online ? 'Conexión disponible' : 'Comprobando conexión',
          child: Container(
            width: 9,
            height: 9,
            decoration: BoxDecoration(
              color: online ? AppColors.success : AppColors.coral,
              shape: BoxShape.circle,
            ),
          ),
        );
      },
    );
  }
}

class _GameStatus extends StatelessWidget {
  const _GameStatus();

  @override
  Widget build(BuildContext context) {
    return Consumer<TimbiricheGame>(
      builder: (context, game, _) {
        return Row(
          children: [
            Expanded(
              child: _ScoreCard(
                name: 'Tutu',
                score: game.scores[Player.tutu]!,
                color: AppColors.coral,
                background: AppColors.coralSoft,
                icon: Icons.favorite_rounded,
                active: game.currentPlayer == Player.tutu,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Column(
                children: [
                  const Text(
                    'TURNO',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: AppColors.muted,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Icon(
                    game.currentPlayer == Player.tutu
                        ? Icons.arrow_back_rounded
                        : Icons.arrow_forward_rounded,
                    color: AppColors.violet,
                  ),
                ],
              ),
            ),
            Expanded(
              child: _ScoreCard(
                name: 'Abuelita',
                score: game.scores[Player.abuelita]!,
                color: AppColors.violet,
                background: AppColors.lavender,
                icon: Icons.auto_awesome_rounded,
                active: game.currentPlayer == Player.abuelita,
              ),
            ),
          ],
        );
      },
    );
  }
}

class _ScoreCard extends StatelessWidget {
  const _ScoreCard({
    required this.name,
    required this.score,
    required this.color,
    required this.background,
    required this.icon,
    required this.active,
  });
  final String name;
  final int score;
  final Color color;
  final Color background;
  final IconData icon;
  final bool active;

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: active ? background : Colors.white.withValues(alpha: .76),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: active ? color : Colors.white,
          width: active ? 1.5 : 1,
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              name,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          Text(
            '$score',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w900,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _BoardCard extends StatelessWidget {
  const _BoardCard();

  @override
  Widget build(BuildContext context) {
    return _Surface(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Consumer<TimbiricheGame>(
            builder: (_, game, _) => AnimatedSwitcher(
              duration: const Duration(milliseconds: 250),
              layoutBuilder: (currentChild, previousChildren) {
                return Stack(
                  alignment: Alignment.center,
                  clipBehavior: Clip.antiAlias,
                  children: [
                    ...previousChildren,
                    if (currentChild != null) currentChild,
                  ],
                );
              },
              transitionBuilder: (child, animation) {
                return FadeTransition(opacity: animation, child: child);
              },
              child: Text(
                game.lastWinnerMessage ??
                    'Une dos puntos. Si cierras un cuadro, vuelves a jugar.',
                key: ValueKey(game.lastWinnerMessage),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: game.lastWinnerMessage == null
                      ? AppColors.muted
                      : AppColors.violetDark,
                  fontWeight: game.lastWinnerMessage == null
                      ? FontWeight.w500
                      : FontWeight.w800,
                  fontSize: 13,
                ),
              ),
            ),
          ),
          const SizedBox(height: 4),
          const Expanded(
            child: ClipRect(
              child: Center(
                child: AspectRatio(aspectRatio: 1, child: GameGrid()),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FooterActions extends StatelessWidget {
  const _FooterActions({this.vertical = false});
  final bool vertical;

  @override
  Widget build(BuildContext context) {
    final help = OutlinedButton.icon(
      onPressed: () => showDialog<void>(
        context: context,
        builder: (_) => const _HowToPlayDialog(),
      ),
      icon: const Icon(Icons.help_outline_rounded),
      label: const Text('Cómo jugar'),
    );
    final restart = FilledButton.icon(
      onPressed: () => context.read<TimbiricheGame>().reset(),
      icon: const Icon(Icons.refresh_rounded),
      label: const Text('Nueva partida'),
    );
    if (vertical) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [help, const SizedBox(height: 8), restart],
      );
    }
    return Row(
      children: [
        Expanded(child: help),
        const SizedBox(width: 10),
        Expanded(child: restart),
      ],
    );
  }
}

class _GameGuideCard extends StatelessWidget {
  const _GameGuideCard();

  @override
  Widget build(BuildContext context) {
    return _Surface(
      padding: const EdgeInsets.all(16),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxHeight < 210;
          if (compact) {
            return Row(
              children: [
                const Icon(
                  Icons.grid_4x4_rounded,
                  size: 26,
                  color: AppColors.violet,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Cierra el cuadro',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 2),
                      const Flexible(
                        child: Text(
                          'Completa el cuarto lado para sumar y volver a jugar.',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            );
          }
          return Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.grid_4x4_rounded,
                size: 42,
                color: AppColors.violet,
              ),
              const SizedBox(height: 14),
              Text(
                'Cierra el cuadro',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              const Flexible(
                child: Text(
                  'Une dos puntos. Si completas el cuarto lado, sumas un punto y vuelves a jugar.',
                  textAlign: TextAlign.center,
                  overflow: TextOverflow.fade,
                ),
              ),
              const SizedBox(height: 18),
              const Text('🦋  🦋  🦋', style: TextStyle(fontSize: 24)),
            ],
          );
        },
      ),
    );
  }
}

class _HowToPlayDialog extends StatelessWidget {
  const _HowToPlayDialog();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      icon: const Icon(Icons.grid_4x4_rounded, color: AppColors.violet),
      title: const Text('Cómo jugar'),
      content: const Text(
        'Por turnos, seleccionen una línea entre dos puntos. Quien complete el cuarto lado de un cuadro suma un punto y juega de nuevo. La partida termina cuando todos los cuadros están completos.',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Entendido'),
        ),
      ],
    );
  }
}

class _Surface extends StatelessWidget {
  const _Surface({required this.child, required this.padding});
  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: .88),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: Colors.white),
        boxShadow: const [
          BoxShadow(
            color: Color(0x1424163A),
            blurRadius: 20,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: child,
    );
  }
}
