// Feature: Speech-to-Text (STT)
// Description: Flutter voice input using browser Web Speech API and speech_to_text package
// Library: speech_to_text, permission_handler

import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:permission_handler/permission_handler.dart';
import 'dart:async';

void main() => runApp(SpeechToTextApp());

class SpeechToTextApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Speech to Text Demo',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: SpeechToTextScreen(),
    );
  }
}

class SpeechToTextScreen extends StatefulWidget {
  @override
  _SpeechToTextScreenState createState() => _SpeechToTextScreenState();
}

class _SpeechToTextScreenState extends State<SpeechToTextScreen> {
  final stt.SpeechToText _speechToText = stt.SpeechToText();
  final TextEditingController _textController = TextEditingController();
  
  bool _isListening = false;
  bool _isAvailable = false;
  String _currentTranscript = '';
  String _previousTranscript = '';
  double _confidence = 0.0;
  Timer? _silenceTimer;
  
  // Configuration
  static const int silenceTimeoutSeconds = 3;
  static const String defaultLocale = 'en-US';
  
  @override
  void initState() {
    super.initState();
    _initializeSpeechToText();
  }

  @override
  void dispose() {
    _silenceTimer?.cancel();
    _speechToText.stop();
    _textController.dispose();
    super.dispose();
  }

  // 1. Initialize Speech-to-Text
  Future<void> _initializeSpeechToText() async {
    try {
      // Check microphone permission
      final permissionStatus = await Permission.microphone.request();
      if (permissionStatus != PermissionStatus.granted) {
        _showPermissionDialog();
        return;
      }

      // Initialize speech recognition
      bool available = await _speechToText.initialize(
        onStatus: _onSpeechStatus,
        onError: _onSpeechError,
        debugLogging: true,
      );

      setState(() {
        _isAvailable = available;
      });

      if (!available) {
        _showErrorSnackBar('Speech recognition not available on this device');
      }
    } catch (e) {
      print('Error initializing speech recognition: $e');
      _showErrorSnackBar('Failed to initialize speech recognition');
    }
  }

  // 2. Start listening for speech
  Future<void> _startListening() async {
    if (!_isAvailable || _isListening) return;

    try {
      // Get available locales
      List<stt.LocaleName> locales = await _speechToText.locales();
      String selectedLocale = defaultLocale;
      
      // Try to find user's preferred locale
      final systemLocale = Localizations.of(context).locale;
      final preferredLocale = '${systemLocale.languageCode}-${systemLocale.countryCode?.toUpperCase()}';
      
      if (locales.any((locale) => locale.localeId == preferredLocale)) {
        selectedLocale = preferredLocale;
      }

      // Reset transcript
      _previousTranscript = _textController.text;
      _currentTranscript = '';

      // Start listening
      await _speechToText.listen(
        onResult: _onSpeechResult,
        listenFor: Duration(minutes: 5), // Max listen duration
        pauseFor: Duration(seconds: silenceTimeoutSeconds),
        partialResults: true, // Get real-time results
        localeId: selectedLocale,
        onSoundLevelChange: _onSoundLevelChange,
        cancelOnError: true,
        listenMode: stt.ListenMode.confirmation,
      );

      setState(() {
        _isListening = true;
      });

      // Start silence detection timer
      _startSilenceTimer();

    } catch (e) {
      print('Error starting speech recognition: $e');
      _showErrorSnackBar('Failed to start speech recognition');
    }
  }

  // 3. Stop listening
  Future<void> _stopListening() async {
    if (!_isListening) return;

    try {
      await _speechToText.stop();
      _silenceTimer?.cancel();
      
      setState(() {
        _isListening = false;
      });

      // Finalize transcript
      if (_currentTranscript.isNotEmpty) {
        _finalizeTranscript();
      }

    } catch (e) {
      print('Error stopping speech recognition: $e');
    }
  }

  // 4. Handle speech recognition results
  void _onSpeechResult(stt.SpeechRecognitionResult result) {
    setState(() {
      _currentTranscript = result.recognizedWords;
      _confidence = result.confidence;
    });

    // Update text field with streaming results
    _updateTextField();

    // Reset silence timer on new speech
    if (result.recognizedWords.isNotEmpty) {
      _startSilenceTimer();
    }

    // Auto-finalize if result is final
    if (result.finalResult) {
      _finalizeTranscript();
      _stopListening();
    }
  }

  // 5. Update text field with streaming transcript
  void _updateTextField() {
    final fullText = _previousTranscript.isEmpty 
        ? _currentTranscript
        : '${_previousTranscript} ${_currentTranscript}';
    
    _textController.text = fullText;
    
    // Move cursor to end
    _textController.selection = TextSelection.fromPosition(
      TextPosition(offset: _textController.text.length),
    );
  }

  // 6. Finalize transcript and add to text
  void _finalizeTranscript() {
    if (_currentTranscript.isNotEmpty) {
      final finalText = _previousTranscript.isEmpty 
          ? _currentTranscript
          : '${_previousTranscript} ${_currentTranscript}';
      
      setState(() {
        _textController.text = finalText;
        _previousTranscript = finalText;
        _currentTranscript = '';
      });
    }
  }

  // 7. Handle silence timeout
  void _startSilenceTimer() {
    _silenceTimer?.cancel();
    _silenceTimer = Timer(Duration(seconds: silenceTimeoutSeconds), () {
      if (_isListening) {
        print('Silence detected, stopping listening...');
        _stopListening();
      }
    });
  }

  // 8. Speech status callbacks
  void _onSpeechStatus(String status) {
    print('Speech status: $status');
    
    if (status == 'done' || status == 'notListening') {
      setState(() {
        _isListening = false;
      });
    }
  }

  void _onSpeechError(stt.SpeechRecognitionError error) {
    print('Speech error: ${error.errorMsg}');
    
    setState(() {
      _isListening = false;
    });

    _showErrorSnackBar('Speech recognition error: ${error.errorMsg}');
  }

  void _onSoundLevelChange(double level) {
    // Optional: Use sound level for visual feedback
    // print('Sound level: $level');
  }

  // 9. UI Helper methods
  void _showPermissionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Microphone Permission Required'),
        content: Text(
          'This app needs microphone access to convert speech to text. '
          'Please grant permission in your device settings.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              openAppSettings();
            },
            child: Text('Open Settings'),
          ),
        ],
      ),
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 3),
      ),
    );
  }

  void _clearText() {
    setState(() {
      _textController.clear();
      _currentTranscript = '';
      _previousTranscript = '';
      _confidence = 0.0;
    });
  }

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isNotEmpty) {
      // Simulate sending message
      _showSuccessSnackBar('Message sent: ${text.substring(0, text.length > 50 ? 50 : text.length)}...');
      _clearText();
    }
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Speech to Text'),
        elevation: 0,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status indicators
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _StatusIndicator(
                          label: 'Available',
                          isActive: _isAvailable,
                          activeColor: Colors.green,
                        ),
                        _StatusIndicator(
                          label: 'Listening',
                          isActive: _isListening,
                          activeColor: Colors.blue,
                        ),
                      ],
                    ),
                    SizedBox(height: 8),
                    if (_confidence > 0)
                      Text(
                        'Confidence: ${(_confidence * 100).toStringAsFixed(1)}%',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 16),

            // Text input field
            Expanded(
              child: Card(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Transcribed Text:',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 8),
                      Expanded(
                        child: TextField(
                          controller: _textController,
                          maxLines: null,
                          expands: true,
                          textAlignVertical: TextAlignVertical.top,
                          decoration: InputDecoration(
                            hintText: 'Tap the microphone button and start speaking...',
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
                // Microphone button
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isAvailable 
                        ? (_isListening ? _stopListening : _startListening)
                        : null,
                    icon: Icon(
                      _isListening ? Icons.mic : Icons.mic_none,
                      color: _isListening ? Colors.red : null,
                    ),
                    label: Text(_isListening ? 'Stop Listening' : 'Start Listening'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _isListening ? Colors.red[50] : null,
                      foregroundColor: _isListening ? Colors.red : null,
                      padding: EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                
                SizedBox(width: 8),
                
                // Clear button
                IconButton(
                  onPressed: _clearText,
                  icon: Icon(Icons.clear),
                  tooltip: 'Clear Text',
                ),
                
                // Send button
                IconButton(
                  onPressed: _textController.text.trim().isNotEmpty ? _sendMessage : null,
                  icon: Icon(Icons.send),
                  tooltip: 'Send Message',
                ),
              ],
            ),

            SizedBox(height: 8),

            // Instructions
            Card(
              color: Colors.blue[50],
              child: Padding(
                padding: EdgeInsets.all(12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Instructions:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[800],
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      '• Tap "Start Listening" and begin speaking\n'
                      '• Speech will be transcribed in real-time\n'
                      '• Listening stops automatically after ${silenceTimeoutSeconds}s of silence\n'
                      '• Tap "Stop Listening" to stop manually\n'
                      '• Use "Clear" to reset and "Send" to submit',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue[700],
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
}

// Helper widget for status indicators
class _StatusIndicator extends StatelessWidget {
  final String label;
  final bool isActive;
  final Color activeColor;

  const _StatusIndicator({
    required this.label,
    required this.isActive,
    required this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isActive ? activeColor : Colors.grey[300],
          ),
        ),
        SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: isActive ? activeColor : Colors.grey[600],
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }
}