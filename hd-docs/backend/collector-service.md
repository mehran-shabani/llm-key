# AnythingLLM Collector - Document Processing Service

## Purpose
The collector is a specialized microservice dedicated to document ingestion, parsing, and text extraction. It handles file uploads, web scraping, and converts various document formats into a standardized format for vector embedding.

## Technologies Used
- **Express.js**: Web framework for REST API endpoints
- **Puppeteer**: Web scraping and automation (headless Chrome)
- **Tesseract.js**: OCR (Optical Character Recognition) for images and PDFs
- **LangChain**: Document loading and text splitting utilities
- **pdf-parse**: PDF text extraction
- **mammoth**: DOCX document processing
- **officeparser**: Office document parsing (PPTX, ODT, ODP)
- **Sharp**: Image processing and optimization
- **node-xlsx**: Excel file processing

## Architecture Overview

### Service Design Pattern
The collector follows a **pipeline architecture** with pluggable converters:

```
Input Document → Validation → Format Detection → Converter → Output JSON
```

### Core Structure
```
collector/
├── index.js              # Main service entry point
├── processSingleFile/     # File processing pipeline
│   ├── index.js          # Main file processor
│   └── convert/          # Format-specific converters
├── processLink/          # Web scraping pipeline
├── processRawText/       # Raw text processing
├── middleware/           # Request validation
├── utils/               # Shared utilities
└── hotdir/              # File upload directory
```

## Core Components

### 1. Main Service (`index.js`)
```javascript
// Microservice setup
const app = express();
const FILE_LIMIT = "3GB";

app.use(cors({ origin: true }));
app.use(bodyParser.json({ limit: FILE_LIMIT }));

// Core endpoints
app.post("/process", [verifyPayloadIntegrity], processSingleFileHandler);
app.post("/process-link", [verifyPayloadIntegrity], processLinkHandler);
app.post("/process-raw-text", [verifyPayloadIntegrity], processRawTextHandler);

// Service runs on port 8888
app.listen(8888, async () => {
  await wipeCollectorStorage();
  console.log(`Document processor app listening on port 8888`);
});
```

**Key Features**:
- **Dedicated port (8888)**: Isolated from main server
- **Large file support**: 3GB file size limit
- **Security middleware**: Payload integrity verification
- **Storage cleanup**: Automatic temporary file cleanup on startup

### 2. File Processing Pipeline

#### File Type Detection and Routing
```javascript
// From processSingleFile/index.js
const fileExtension = path.extname(fullFilePath).toLowerCase();
let processFileAs = fileExtension;

if (!SUPPORTED_FILETYPE_CONVERTERS.hasOwnProperty(fileExtension)) {
  if (isTextType(fullFilePath)) {
    processFileAs = ".txt"; // Fallback to text processing
  } else {
    return { success: false, reason: "File extension not supported" };
  }
}

const FileTypeProcessor = require(SUPPORTED_FILETYPE_CONVERTERS[processFileAs]);
return await FileTypeProcessor({ fullFilePath, filename, options });
```

#### Supported File Formats
```javascript
// From utils/constants.js
const SUPPORTED_FILETYPE_CONVERTERS = {
  // Text formats
  ".txt": "./convert/asTxt.js",
  ".md": "./convert/asTxt.js", 
  ".html": "./convert/asTxt.js",
  
  // Office documents
  ".pdf": "./convert/asPDF/index.js",
  ".docx": "./convert/asDocx.js",
  ".pptx": "./convert/asOfficeMime.js",
  ".xlsx": "./convert/asXlsx.js",
  
  // Media files
  ".mp3": "./convert/asAudio.js",
  ".wav": "./convert/asAudio.js",
  ".png": "./convert/asImage.js",
  ".jpg": "./convert/asImage.js",
  
  // Other formats
  ".epub": "./convert/asEPub.js",
  ".mbox": "./convert/asMbox.js"
};
```

### 3. Document Converter Architecture

#### PDF Processing with OCR Fallback
```javascript
// From convert/asPDF/index.js
async function asPdf({ fullFilePath, filename, options = {} }) {
  const pdfLoader = new PDFLoader(fullFilePath, { splitPages: true });
  let docs = await pdfLoader.load();
  
  // OCR fallback for image-based PDFs
  if (docs.length === 0) {
    console.log(`No text content found for ${filename}. Will attempt OCR parse.`);
    docs = await new OCRLoader({
      targetLanguages: options?.ocr?.langList,
    }).ocrPDF(fullFilePath);
  }
  
  // Process each page
  const pageContent = [];
  for (const doc of docs) {
    if (doc.pageContent?.length) {
      pageContent.push(doc.pageContent);
    }
  }
  
  // Generate standardized document object
  const data = {
    id: v4(),
    url: "file://" + fullFilePath,
    title: filename,
    docAuthor: docs[0]?.metadata?.pdf?.info?.Creator || "no author found",
    pageContent: pageContent.join(""),
    token_count_estimate: tokenizeString(content),
    // ... other metadata
  };
  
  return { success: true, documents: [document] };
}
```

#### Image OCR Processing
```javascript
// From convert/asImage.js
async function asImage({ fullFilePath, filename, options = {} }) {
  let content = await new OCRLoader({
    targetLanguages: options?.ocr?.langList,
  }).ocrImage(fullFilePath);
  
  if (!content?.length) {
    trashFile(fullFilePath);
    return { success: false, reason: "No text content found" };
  }
  
  // Generate document with OCR'd text
  const data = {
    id: v4(),
    pageContent: content,
    token_count_estimate: tokenizeString(content),
    // ... metadata
  };
  
  return { success: true, documents: [document] };
}
```

### 4. Web Scraping Pipeline

#### Puppeteer-Based Scraping
```javascript
// From processLink/convert/generic.js
async function scrapeGenericUrl({ link, captureAs = "text", scraperHeaders = {} }) {
  const loader = new PuppeteerWebBaseLoader(link, {
    launchOptions: {
      headless: "new",
      ignoreHTTPSErrors: true,
    },
    gotoOptions: {
      waitUntil: "networkidle2", // Wait for network to be idle
    },
    async evaluate(page, browser) {
      const result = await page.evaluate((captureAs) => {
        if (captureAs === "text") return document.body.innerText;
        if (captureAs === "html") return document.documentElement.innerHTML;
        return document.body.innerText;
      }, captureAs);
      await browser.close();
      return result;
    },
  });
  
  // Custom header support
  if (Object.keys(scraperHeaders).length > 0) {
    loader.scrape = async function () {
      const page = await browser.newPage();
      await page.setExtraHTTPHeaders(scraperHeaders);
      // ... custom scraping logic
    };
  }
  
  const docs = await loader.load();
  return docs.join(" ");
}
```

**Scraping Features**:
- **Headless Chrome**: Full JavaScript execution
- **Custom headers**: Support for authentication and user agents
- **Network idle waiting**: Ensures dynamic content loads
- **Fallback to fetch**: If Puppeteer fails, falls back to simple HTTP request
- **Flexible output**: Can capture as text, HTML, or JSON

### 5. Security and Validation

#### Payload Integrity Verification
```javascript
// From middleware/verifyIntegrity.js
function verifyPayloadIntegrity(request, response, next) {
  const comKey = new CommunicationKey();
  
  if (process.env.NODE_ENV === "development") {
    next(); // Skip in development
    return;
  }
  
  const signature = request.header("X-Integrity");
  if (!signature) {
    return response.status(400).json({ msg: 'Failed integrity signature check.' });
  }
  
  const validSignedPayload = comKey.verify(signature, request.body);
  if (!validSignedPayload) {
    return response.status(400).json({ msg: 'Failed integrity signature check.' });
  }
  
  next();
}
```

#### Path Traversal Protection
```javascript
// From processSingleFile/index.js
const fullFilePath = path.resolve(WATCH_DIRECTORY, normalizePath(targetFilename));

if (!isWithin(path.resolve(WATCH_DIRECTORY), fullFilePath)) {
  return {
    success: false,
    reason: "Filename is not a valid path to process.",
    documents: [],
  };
}
```

### 6. Document Output Format

#### Standardized Document Schema
```javascript
const documentSchema = {
  id: v4(),                           // Unique identifier
  url: "file://" + fullFilePath,      // File location
  title: filename,                    // Display name
  docAuthor: "extracted author",      // Document author
  description: "extracted description", // Document description
  docSource: "pdf file uploaded by user", // Source type
  chunkSource: "",                    // Chunk identifier
  published: createdDate(fullFilePath), // Creation date
  wordCount: content.split(" ").length, // Word count
  pageContent: extractedText,         // Main content
  token_count_estimate: tokenizeString(content) // Token estimate
};
```

## Notable Technical Decisions

### 1. **Microservice Isolation**
```javascript
// Separate port and process
app.listen(8888, async () => {
  await wipeCollectorStorage();
  console.log(`Document processor app listening on port 8888`);
});
```
**Rationale**: 
- Isolates resource-intensive document processing
- Prevents main server crashes from document processing failures
- Enables independent scaling and deployment

### 2. **OCR Fallback Strategy**
```javascript
// PDF processing with OCR fallback
if (docs.length === 0) {
  console.log(`No text content found. Will attempt OCR parse.`);
  docs = await new OCRLoader().ocrPDF(fullFilePath);
}
```
**Rationale**: Handles image-based PDFs and scanned documents that don't contain extractable text

### 3. **Multi-Stage Web Scraping**
```javascript
// Puppeteer with fetch fallback
try {
  // Try Puppeteer first (handles JavaScript)
  const docs = await loader.load();
  return docs.join(" ");
} catch (error) {
  // Fallback to simple HTTP request
  const pageText = await fetch(link).then(res => res.text());
  return pageText;
}
```
**Rationale**: Balances functionality (JavaScript execution) with reliability (simple HTTP fallback)

### 4. **Temporary File Management**
```javascript
// Automatic cleanup after processing
const document = writeToServerDocuments({ data, filename });
trashFile(fullFilePath); // Clean up temporary file
```
**Rationale**: Prevents disk space accumulation from temporary processing files

### 5. **Token Count Estimation**
```javascript
token_count_estimate: tokenizeString(content)
```
**Rationale**: Pre-calculates token counts for embedding cost estimation and chunking decisions

### 6. **Flexible Processing Options**
```javascript
// Parse-only mode for preview
const document = writeToServerDocuments({
  data,
  filename,
  options: { parseOnly: options.parseOnly } // Don't persist if just previewing
});
```
**Rationale**: Supports document preview without committing to storage

## Integration Points

### Communication with Main Server
- **Integrity verification**: Cryptographic signatures prevent unauthorized access
- **Standardized responses**: Consistent JSON format across all processors
- **Error handling**: Detailed error messages for debugging

### File System Integration
- **Hot directory**: `collector/hotdir/` for file uploads
- **Server documents**: Processed files saved to `server/storage/documents/`
- **Vector cache**: Integration with vector database caching system

This collector architecture enables AnythingLLM to handle diverse document types while maintaining security, reliability, and performance isolation from the main application server.