// Feature: Text-to-Speech (TTS) - Flutter Frontend
// Description: Flutter client for text-to-speech with multiple provider support
// Library: flutter_tts, http, audioplayers

import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'dart:convert';
import 'dart:typed_data';

void main() => runApp(TextToSpeechApp());

class TextToSpeechApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Text to Speech Demo',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: TextToSpeechScreen(),
    );
  }
}

class TextToSpeechScreen extends StatefulWidget {
  @override
  _TextToSpeechScreenState createState() => _TextToSpeechScreenState();
}

class _TextToSpeechScreenState extends State<TextToSpeechScreen> {
  final TextEditingController _textController = TextEditingController();
  final FlutterTts _flutterTts = FlutterTts();
  final AudioPlayer _audioPlayer = AudioPlayer();
  
  // TTS State
  bool _isNativeSpeaking = false;
  bool _isServerProcessing = false;
  bool _isPlayingServerAudio = false;
  
  // Configuration
  String _selectedProvider = 'native';
  String _selectedVoice = '';
  double _speechRate = 0.5;
  double _speechVolume = 1.0;
  double _speechPitch = 1.0;
  
  // Available providers and voices
  List<String> _providers = ['native', 'openai', 'elevenlabs', 'google'];
  List<Map<String, dynamic>> _availableVoices = [];
  List<Map<String, dynamic>> _serverVoices = [];
  
  // Server configuration
  static const String serverUrl = 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    _initializeTTS();
    _loadServerProviders();
  }

  @override
  void dispose() {
    _flutterTts.stop();
    _audioPlayer.dispose();
    super.dispose();
  }

  // 1. Initialize native TTS
  Future<void> _initializeTTS() async {
    try {
      // Configure TTS settings
      await _flutterTts.setLanguage("en-US");
      await _flutterTts.setSpeechRate(_speechRate);
      await _flutterTts.setVolume(_speechVolume);
      await _flutterTts.setPitch(_speechPitch);

      // Set up TTS callbacks
      _flutterTts.setStartHandler(() {
        setState(() => _isNativeSpeaking = true);
      });

      _flutterTts.setCompletionHandler(() {
        setState(() => _isNativeSpeaking = false);
      });

      _flutterTts.setErrorHandler((msg) {
        print('TTS Error: $msg');
        setState(() => _isNativeSpeaking = false);
        _showErrorSnackBar('TTS Error: $msg');
      });

      // Load available voices
      await _loadNativeVoices();

    } catch (e) {
      print('Error initializing TTS: $e');
      _showErrorSnackBar('Failed to initialize TTS');
    }
  }

  // 2. Load native TTS voices
  Future<void> _loadNativeVoices() async {
    try {
      List<dynamic> voices = await _flutterTts.getVoices;
      
      setState(() {
        _availableVoices = voices.map((voice) => {
          'name': voice['name'] ?? 'Unknown',
          'locale': voice['locale'] ?? 'en-US',
        }).toList();
        
        if (_availableVoices.isNotEmpty && _selectedVoice.isEmpty) {
          _selectedVoice = _availableVoices.first['name'];
        }
      });

    } catch (e) {
      print('Error loading voices: $e');
    }
  }

  // 3. Load server TTS providers and voices
  Future<void> _loadServerProviders() async {
    try {
      // Load available providers
      final response = await http.get(
        Uri.parse('$serverUrl/tts/providers/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final providers = List<Map<String, dynamic>>.from(data['providers']);
        
        setState(() {
          _providers = ['native', ...providers.map((p) => p['name'] as String)];
        });
      }

    } catch (e) {
      print('Error loading server providers: $e');
    }
  }

  // 4. Load voices for selected server provider
  Future<void> _loadServerVoices(String provider) async {
    try {
      final response = await http.get(
        Uri.parse('$serverUrl/tts/voices/$provider/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _serverVoices = List<Map<String, dynamic>>.from(data['voices']);
          if (_serverVoices.isNotEmpty && _selectedVoice.isEmpty) {
            _selectedVoice = _serverVoices.first['voice_id'];
          }
        });
      }

    } catch (e) {
      print('Error loading server voices: $e');
      _showErrorSnackBar('Failed to load voices for $provider');
    }
  }

  // 5. Speak using native TTS
  Future<void> _speakNative() async {
    final text = _textController.text.trim();
    if (text.isEmpty) {
      _showErrorSnackBar('Please enter some text');
      return;
    }

    try {
      if (_isNativeSpeaking) {
        await _flutterTts.stop();
        return;
      }

      // Set voice if selected
      if (_selectedVoice.isNotEmpty) {
        await _flutterTts.setVoice({
          'name': _selectedVoice,
          'locale': 'en-US'
        });
      }

      // Update TTS settings
      await _flutterTts.setSpeechRate(_speechRate);
      await _flutterTts.setVolume(_speechVolume);
      await _flutterTts.setPitch(_speechPitch);

      await _flutterTts.speak(text);

    } catch (e) {
      print('Error speaking: $e');
      _showErrorSnackBar('Failed to speak text');
    }
  }

  // 6. Generate and play server TTS
  Future<void> _speakServer() async {
    final text = _textController.text.trim();
    if (text.isEmpty) {
      _showErrorSnackBar('Please enter some text');
      return;
    }

    setState(() => _isServerProcessing = true);

    try {
      final requestBody = {
        'text': text,
        'provider': _selectedProvider,
        'voice_id': _selectedVoice,
        'format': 'mp3',
      };

      final response = await http.post(
        Uri.parse('$serverUrl/tts/synthesize/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(requestBody),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        if (data['success']) {
          // Play the generated audio
          await _playServerAudio(data['audio_url']);
          
          _showSuccessSnackBar(
            'Audio generated in ${data['processing_time_ms']}ms '
            'using ${data['provider']} (${data['voice_used']})'
          );
        } else {
          _showErrorSnackBar('Server TTS failed: ${data['error']}');
        }
      } else {
        final error = json.decode(response.body);
        _showErrorSnackBar('Server error: ${error['error']}');
      }

    } catch (e) {
      print('Error with server TTS: $e');
      _showErrorSnackBar('Failed to connect to TTS server');
    } finally {
      setState(() => _isServerProcessing = false);
    }
  }

  // 7. Play audio from server
  Future<void> _playServerAudio(String audioUrl) async {
    try {
      setState(() => _isPlayingServerAudio = true);

      // Configure audio player
      _audioPlayer.onPlayerStateChanged.listen((PlayerState state) {
        if (state == PlayerState.completed || state == PlayerState.stopped) {
          setState(() => _isPlayingServerAudio = false);
        }
      });

      // Play the audio
      await _audioPlayer.play(UrlSource('$serverUrl$audioUrl'));

    } catch (e) {
      print('Error playing server audio: $e');
      _showErrorSnackBar('Failed to play generated audio');
      setState(() => _isPlayingServerAudio = false);
    }
  }

  // 8. Stop all audio
  Future<void> _stopAll() async {
    await _flutterTts.stop();
    await _audioPlayer.stop();
    setState(() {
      _isNativeSpeaking = false;
      _isPlayingServerAudio = false;
    });
  }

  // 9. UI Helper methods
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 3),
      ),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 3),
      ),
    );
  }

  Widget _buildVoiceSelector() {
    List<Map<String, dynamic>> voices = _selectedProvider == 'native' 
        ? _availableVoices 
        : _serverVoices;

    if (voices.isEmpty) {
      return Text('No voices available', style: TextStyle(color: Colors.grey));
    }

    return DropdownButton<String>(
      value: _selectedVoice.isNotEmpty ? _selectedVoice : null,
      hint: Text('Select Voice'),
      isExpanded: true,
      onChanged: (String? newValue) {
        setState(() => _selectedVoice = newValue ?? '');
      },
      items: voices.map<DropdownMenuItem<String>>((voice) {
        String voiceId = _selectedProvider == 'native' ? voice['name'] : voice['voice_id'];
        String voiceName = voice['name'] ?? voiceId;
        String language = voice['language'] ?? voice['locale'] ?? '';
        
        return DropdownMenuItem<String>(
          value: voiceId,
          child: Text('$voiceName ($language)'),
        );
      }).toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Text to Speech'),
        elevation: 0,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Provider selection
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('TTS Provider:', style: TextStyle(fontWeight: FontWeight.bold)),
                    SizedBox(height: 8),
                    DropdownButton<String>(
                      value: _selectedProvider,
                      isExpanded: true,
                      onChanged: (String? newValue) {
                        setState(() {
                          _selectedProvider = newValue ?? 'native';
                          _selectedVoice = '';
                          _serverVoices.clear();
                        });
                        
                        if (newValue != 'native') {
                          _loadServerVoices(newValue!);
                        }
                      },
                      items: _providers.map<DropdownMenuItem<String>>((String value) {
                        return DropdownMenuItem<String>(
                          value: value,
                          child: Text(value.toUpperCase()),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 16),

            // Voice selection
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Voice:', style: TextStyle(fontWeight: FontWeight.bold)),
                    SizedBox(height: 8),
                    _buildVoiceSelector(),
                  ],
                ),
              ),
            ),

            SizedBox(height: 16),

            // Native TTS settings (only show for native provider)
            if (_selectedProvider == 'native') ...[
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Settings:', style: TextStyle(fontWeight: FontWeight.bold)),
                      
                      Text('Speech Rate: ${_speechRate.toStringAsFixed(1)}'),
                      Slider(
                        value: _speechRate,
                        min: 0.1,
                        max: 1.0,
                        divisions: 9,
                        onChanged: (value) => setState(() => _speechRate = value),
                      ),
                      
                      Text('Volume: ${_speechVolume.toStringAsFixed(1)}'),
                      Slider(
                        value: _speechVolume,
                        min: 0.0,
                        max: 1.0,
                        divisions: 10,
                        onChanged: (value) => setState(() => _speechVolume = value),
                      ),
                      
                      Text('Pitch: ${_speechPitch.toStringAsFixed(1)}'),
                      Slider(
                        value: _speechPitch,
                        min: 0.5,
                        max: 2.0,
                        divisions: 15,
                        onChanged: (value) => setState(() => _speechPitch = value),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 16),
            ],

            // Text input
            Expanded(
              child: Card(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Text to Speak:', style: TextStyle(fontWeight: FontWeight.bold)),
                      SizedBox(height: 8),
                      Expanded(
                        child: TextField(
                          controller: _textController,
                          maxLines: null,
                          expands: true,
                          textAlignVertical: TextAlignVertical.top,
                          decoration: InputDecoration(
                            hintText: 'Enter text to convert to speech...',
                            border: OutlineInputBorder(),
                            contentPadding: EdgeInsets.all(12),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            SizedBox(height: 16),

            // Control buttons
            Row(
              children: [
                // Speak button
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: (_isNativeSpeaking || _isServerProcessing || _isPlayingServerAudio) 
                        ? null 
                        : (_selectedProvider == 'native' ? _speakNative : _speakServer),
                    icon: _isServerProcessing 
                        ? SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                        : Icon(_isNativeSpeaking || _isPlayingServerAudio ? Icons.volume_up : Icons.play_arrow),
                    label: Text(_getButtonText()),
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                
                SizedBox(width: 8),
                
                // Stop button
                ElevatedButton.icon(
                  onPressed: (_isNativeSpeaking || _isPlayingServerAudio) ? _stopAll : null,
                  icon: Icon(Icons.stop),
                  label: Text('Stop'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red[50],
                    foregroundColor: Colors.red,
                    padding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                  ),
                ),
              ],
            ),

            SizedBox(height: 8),

            // Status indicator
            Card(
              color: Colors.blue[50],
              child: Padding(
                padding: EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    Icon(
                      _isNativeSpeaking || _isPlayingServerAudio 
                          ? Icons.volume_up 
                          : _isServerProcessing 
                              ? Icons.hourglass_empty 
                              : Icons.volume_off,
                      color: Colors.blue[700],
                      size: 16,
                    ),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _getStatusText(),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue[700],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getButtonText() {
    if (_isServerProcessing) return 'Processing...';
    if (_isNativeSpeaking) return 'Speaking (Native)';
    if (_isPlayingServerAudio) return 'Playing (Server)';
    return 'Speak Text';
  }

  String _getStatusText() {
    if (_isServerProcessing) return 'Generating audio on server...';
    if (_isNativeSpeaking) return 'Speaking using native TTS';
    if (_isPlayingServerAudio) return 'Playing server-generated audio';
    return 'Ready to speak';
  }
}