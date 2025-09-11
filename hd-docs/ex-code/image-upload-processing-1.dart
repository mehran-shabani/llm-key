// Feature: Image Upload & Processing - Flutter Frontend
// Description: Flutter image upload with drag-drop, camera capture, and processing
// Library: image_picker, file_picker, dio, image

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import 'package:image/image.dart' as img;
import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';

void main() => runApp(ImageUploadApp());

class ImageUploadApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Image Upload & Processing',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: ImageUploadScreen(),
    );
  }
}

class ImageUploadScreen extends StatefulWidget {
  @override
  _ImageUploadScreenState createState() => _ImageUploadScreenState();
}

class _ImageUploadScreenState extends State<ImageUploadScreen> {
  final ImagePicker _picker = ImagePicker();
  final Dio _dio = Dio();
  
  List<ProcessedImage> _images = [];
  bool _isProcessing = false;
  
  // Server configuration
  static const String serverUrl = 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    _loadProcessedImages();
  }

  // 1. Load previously processed images
  Future<void> _loadProcessedImages() async {
    try {
      final response = await _dio.get('$serverUrl/images/processed/');
      
      if (response.statusCode == 200) {
        final data = response.data;
        setState(() {
          _images = (data['images'] as List)
              .map((item) => ProcessedImage.fromJson(item))
              .toList();
        });
      }
    } catch (e) {
      print('Error loading processed images: $e');
    }
  }

  // 2. Pick image from gallery
  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      
      if (image != null) {
        await _processAndUploadImage(File(image.path), 'gallery');
      }
    } catch (e) {
      _showErrorSnackBar('Failed to pick image: $e');
    }
  }

  // 3. Take photo with camera
  Future<void> _takePhotoWithCamera() async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );
      
      if (photo != null) {
        await _processAndUploadImage(File(photo.path), 'camera');
      }
    } catch (e) {
      _showErrorSnackBar('Failed to take photo: $e');
    }
  }

  // 4. Pick multiple images
  Future<void> _pickMultipleImages() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: true,
        allowedExtensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
      );

      if (result != null) {
        setState(() => _isProcessing = true);
        
        for (PlatformFile file in result.files) {
          if (file.path != null) {
            await _processAndUploadImage(File(file.path!), 'file_picker');
          }
        }
        
        setState(() => _isProcessing = false);
      }
    } catch (e) {
      setState(() => _isProcessing = false);
      _showErrorSnackBar('Failed to pick images: $e');
    }
  }

  // 5. Process and upload image
  Future<void> _processAndUploadImage(File imageFile, String source) async {
    try {
      setState(() => _isProcessing = true);

      // Get image info
      final imageBytes = await imageFile.readAsBytes();
      final decodedImage = img.decodeImage(imageBytes);
      
      if (decodedImage == null) {
        throw Exception('Could not decode image');
      }

      // Create form data
      FormData formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(
          imageFile.path,
          filename: imageFile.path.split('/').last,
        ),
        'source': source,
        'width': decodedImage.width,
        'height': decodedImage.height,
        'process_ocr': true,
        'resize_max_width': 800,
      });

      // Upload to server
      final response = await _dio.post(
        '$serverUrl/images/upload-process/',
        data: formData,
        options: Options(
          headers: {'Content-Type': 'multipart/form-data'},
          sendTimeout: Duration(seconds: 30),
          receiveTimeout: Duration(seconds: 60),
        ),
        onSendProgress: (sent, total) {
          print('Upload progress: ${(sent / total * 100).toStringAsFixed(1)}%');
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        
        if (data['success']) {
          final processedImage = ProcessedImage.fromJson(data['image']);
          
          setState(() {
            _images.insert(0, processedImage);
          });
          
          _showSuccessSnackBar(
            'Image processed successfully! '
            '${data['image']['ocr_text'] != null ? 'Text extracted' : 'No text found'}'
          );
        } else {
          _showErrorSnackBar('Server error: ${data['error']}');
        }
      } else {
        _showErrorSnackBar('Upload failed: ${response.statusMessage}');
      }

    } catch (e) {
      _showErrorSnackBar('Failed to process image: $e');
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  // 6. Delete processed image
  Future<void> _deleteImage(String imageId) async {
    try {
      final response = await _dio.delete('$serverUrl/images/$imageId/');
      
      if (response.statusCode == 200) {
        setState(() {
          _images.removeWhere((img) => img.id == imageId);
        });
        _showSuccessSnackBar('Image deleted successfully');
      } else {
        _showErrorSnackBar('Failed to delete image');
      }
    } catch (e) {
      _showErrorSnackBar('Error deleting image: $e');
    }
  }

  // 7. Show image details dialog
  void _showImageDetails(ProcessedImage image) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(image.filename),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (image.thumbnailUrl.isNotEmpty)
                Image.network(
                  '$serverUrl${image.thumbnailUrl}',
                  height: 200,
                  fit: BoxFit.contain,
                ),
              SizedBox(height: 16),
              _buildDetailRow('Size', '${image.width} x ${image.height}'),
              _buildDetailRow('File Size', '${(image.fileSizeBytes / 1024).toStringAsFixed(1)} KB'),
              _buildDetailRow('Format', image.format.toUpperCase()),
              _buildDetailRow('Source', image.source),
              _buildDetailRow('Upload Date', image.createdAt.toString().split('.')[0]),
              
              if (image.ocrText != null && image.ocrText!.isNotEmpty) ...[
                SizedBox(height: 16),
                Text('Extracted Text:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Container(
                  padding: EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    image.ocrText!,
                    style: TextStyle(fontSize: 12),
                  ),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _deleteImage(image.id);
            },
            child: Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  // 8. UI Helper methods
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
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Image Upload & Processing'),
        elevation: 0,
        actions: [
          IconButton(
            onPressed: _loadProcessedImages,
            icon: Icon(Icons.refresh),
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          // Upload options
          Container(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _pickImageFromGallery,
                    icon: Icon(Icons.photo_library),
                    label: Text('Gallery'),
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _takePhotoWithCamera,
                    icon: Icon(Icons.camera_alt),
                    label: Text('Camera'),
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _pickMultipleImages,
                    icon: Icon(Icons.file_upload),
                    label: Text('Multiple'),
                  ),
                ),
              ],
            ),
          ),

          // Processing indicator
          if (_isProcessing)
            Container(
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  CircularProgressIndicator(),
                  SizedBox(width: 16),
                  Text('Processing images...'),
                ],
              ),
            ),

          // Images grid
          Expanded(
            child: _images.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.image, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(
                          'No images uploaded yet',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey[600],
                          ),
                        ),
                        SizedBox(height: 8),
                        Text(
                          'Tap one of the buttons above to upload images',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ),
                  )
                : GridView.builder(
                    padding: EdgeInsets.all(16),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      childAspectRatio: 0.8,
                    ),
                    itemCount: _images.length,
                    itemBuilder: (context, index) {
                      final image = _images[index];
                      return _ImageCard(
                        image: image,
                        onTap: () => _showImageDetails(image),
                        onDelete: () => _deleteImage(image.id),
                        serverUrl: serverUrl,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

// Image data model
class ProcessedImage {
  final String id;
  final String filename;
  final String format;
  final int width;
  final int height;
  final int fileSizeBytes;
  final String source;
  final String? ocrText;
  final int? wordCount;
  final String thumbnailUrl;
  final String fullImageUrl;
  final DateTime createdAt;

  ProcessedImage({
    required this.id,
    required this.filename,
    required this.format,
    required this.width,
    required this.height,
    required this.fileSizeBytes,
    required this.source,
    this.ocrText,
    this.wordCount,
    required this.thumbnailUrl,
    required this.fullImageUrl,
    required this.createdAt,
  });

  factory ProcessedImage.fromJson(Map<String, dynamic> json) {
    return ProcessedImage(
      id: json['id'],
      filename: json['filename'],
      format: json['format'],
      width: json['width'],
      height: json['height'],
      fileSizeBytes: json['file_size_bytes'],
      source: json['source'],
      ocrText: json['ocr_text'],
      wordCount: json['word_count'],
      thumbnailUrl: json['thumbnail_url'],
      fullImageUrl: json['full_image_url'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

// Image card widget
class _ImageCard extends StatelessWidget {
  final ProcessedImage image;
  final VoidCallback onTap;
  final VoidCallback onDelete;
  final String serverUrl;

  const _ImageCard({
    required this.image,
    required this.onTap,
    required this.onDelete,
    required this.serverUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image thumbnail
            Expanded(
              flex: 3,
              child: ClipRRect(
                borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
                child: image.thumbnailUrl.isNotEmpty
                    ? Image.network(
                        '$serverUrl${image.thumbnailUrl}',
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            color: Colors.grey[300],
                            child: Icon(Icons.broken_image, color: Colors.grey),
                          );
                        },
                      )
                    : Container(
                        color: Colors.grey[300],
                        child: Icon(Icons.image, color: Colors.grey),
                      ),
              ),
            ),

            // Image info
            Expanded(
              flex: 2,
              child: Padding(
                padding: EdgeInsets.all(8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      image.filename,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    
                    SizedBox(height: 4),
                    
                    Text(
                      '${image.width} x ${image.height}',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ),
                    ),
                    
                    Text(
                      '${(image.fileSizeBytes / 1024).toStringAsFixed(1)} KB',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ),
                    ),
                    
                    SizedBox(height: 4),
                    
                    // OCR indicator
                    if (image.ocrText != null && image.ocrText!.isNotEmpty)
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.green[100],
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          'Text: ${image.wordCount} words',
                          style: TextStyle(
                            fontSize: 9,
                            color: Colors.green[700],
                          ),
                        ),
                      )
                    else
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          'No text',
                          style: TextStyle(
                            fontSize: 9,
                            color: Colors.grey[600],
                          ),
                        ),
                      ),
                    
                    Spacer(),
                    
                    // Action buttons
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        IconButton(
                          onPressed: onDelete,
                          icon: Icon(Icons.delete, size: 16),
                          iconSize: 16,
                          padding: EdgeInsets.all(4),
                          constraints: BoxConstraints(),
                          color: Colors.red,
                        ),
                      ],
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