import { promises as fs } from 'fs';
import path from 'path';
import { createCanvas } from 'canvas';
import { createWorker } from 'tesseract.js';
import { createObjectCsvWriter as createCsvWriter } from 'csv-writer';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

//import pdf from 'pdfjs-dist/legacy/build/pdf.js';
//const { getDocument } = pdf;

// require to isntall: npm install pdfjs-dist@2.16.105
import pdfjsLib from 'pdfjs-dist/legacy/build/pdf.js';
pdfjsLib.GlobalWorkerOptions.workerSrc = path.join(__dirname, 'node_modules/pdfjs-dist/legacy/build/pdf.worker.js');
const { getDocument } = pdfjsLib;

async function extractSearchableText(pdf) {
    const textContent = [];
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const content = await page.getTextContent();
        textContent.push({
            pageNumber: pageNum,
            text: content.items.map(item => item.str.trim()).join(' ')
        });
    }
    return textContent;
}

async function convertToImage(page) {
    const viewport = page.getViewport({ scale: 1.5 });
    const canvas = createCanvas(viewport.width, viewport.height);
    const context = canvas.getContext('2d');
    
    await page.render({
        canvasContext: context,
        viewport: viewport,
    }).promise;
    
    return canvas.toBuffer('image/png');
}

async function processDirectory(dirPath, language = 'eng') {
    const resultsDir = 'results';
    await fs.mkdir(resultsDir, { recursive: true });

    const searchableWriter = createCsvWriter({
        path: path.join(resultsDir, 'searchable_text.csv'),
        header: [
            { id: 'filename', title: 'Filename' },
            { id: 'pageNumber', title: 'Page Number' },
            { id: 'text', title: 'Text Content' }
        ]
    });

    const ocrWriter = createCsvWriter({
        path: path.join(resultsDir, 'ocr_text.csv'),
        header: [
            { id: 'filename', title: 'Filename' },
            { id: 'pageNumber', title: 'Page Number' },
            { id: 'text', title: 'OCR Text' }
        ]
    });

    const tesseractWorker = await createWorker('eng+heb');
    

    try {
        const files = (await fs.readdir(dirPath))
            .filter(file => path.extname(file).toLowerCase() === '.pdf');

        for (const file of files) {
            console.log(`Processing ${file}...`);
            const filePath = path.join(dirPath, file);
            const dataBuffer = await fs.readFile(filePath);
            
            const pdf = await getDocument({
                data: new Uint8Array(dataBuffer),
                password: '',
                useWorkerFetch: false,
                isEvalSupported: false,
                useSystemFonts: true
            }).promise;

            const searchableContent = await extractSearchableText(pdf);
            
            await searchableWriter.writeRecords(
                searchableContent.map(item => ({
                    filename: file,
                    ...item
                }))
            );
            
            // Extracting OCR text for each page of the PDF document
            // This process involves converting each page to an image and then using Tesseract.js for OCR
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                const page = await pdf.getPage(pageNum);
                const image = await convertToImage(page);
                
                const { data: { text } } = await tesseractWorker.recognize(image);
                
                await ocrWriter.writeRecords([{
                    filename: file,
                    pageNumber: pageNum,
                    text: text.trim()
                }]);
            }
            
            console.log(`Completed processing ${file}`);
        }

    } catch (error) {
        console.error('Error processing PDFs:', error);
        throw error;
    } finally {
        await tesseractWorker.terminate();
    }
}

async function main() {
    const directoryPath = process.argv[2];
    const language = process.argv[3] || 'eng';
    
    if (!directoryPath) {
        console.error('Please provide a directory path');
        process.exit(1);
    }
    
    try {
        await processDirectory(directoryPath, language);
        console.log('Processing complete');
    } catch (error) {
        console.error('Processing failed:', error);
        process.exit(1);
    }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
    main();
}

export { processDirectory };