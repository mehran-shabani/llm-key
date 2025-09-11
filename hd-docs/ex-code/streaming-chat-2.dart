// Feature: Streaming Chat Interface
// Description: Flutter client for receiving streamed chat from Django SSE endpoint
// Library: http package for SSE, Flutter

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

void main() => runApp(StreamingChatApp());

class StreamingChatApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ChatScreen(),
      theme: ThemeData(primarySwatch: Colors.blue),
    );
  }
}

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();
  bool _isStreaming = false;

  // 1. Send message and listen to SSE stream
  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true));
      _messages.add(ChatMessage(text: '', isUser: false, isStreaming: true));
      _isStreaming = true;
    });
    _messageController.clear();

    // 2. Start SSE stream
    final request = http.Request('POST', Uri.parse('http://localhost:8000/workspace/demo/stream-chat/'));
    request.headers['Content-Type'] = 'application/json';
    request.body = json.encode({'message': message});
    
    final response = await request.send();
    
    // 3. Process streaming response
    String assistantResponse = '';
    await for (String line in response.stream.transform(utf8.decoder).transform(LineSplitter())) {
      if (line.startsWith('data: ')) {
        final data = json.decode(line.substring(6));
        if (data['type'] == 'textResponseChunk') {
          assistantResponse += data['textResponse'];
          setState(() {
            _messages.last = ChatMessage(text: assistantResponse, isUser: false);
          });
          _scrollToBottom();
        }
      }
    }
    
    setState(() => _isStreaming = false);
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Streaming Chat')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: _messages.length,
              itemBuilder: (context, index) => ChatBubble(message: _messages[index]),
            ),
          ),
          Container(
            padding: EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(hintText: 'Type a message...'),
                    enabled: !_isStreaming,
                  ),
                ),
                IconButton(
                  onPressed: _isStreaming ? null : _sendMessage,
                  icon: Icon(_isStreaming ? Icons.hourglass_empty : Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final bool isStreaming;
  
  ChatMessage({required this.text, required this.isUser, this.isStreaming = false});
}

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  
  ChatBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: Row(
        mainAxisAlignment: message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.7),
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: message.isUser ? Colors.blue : Colors.grey[300],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              message.text.isEmpty && message.isStreaming ? 'Typing...' : message.text,
              style: TextStyle(color: message.isUser ? Colors.white : Colors.black),
            ),
          ),
        ],
      ),
    );
  }
}