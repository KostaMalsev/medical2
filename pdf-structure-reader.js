const fs = require('fs').promises;
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf.js');

class EnhancedPDFReader {
    constructor() {
        pdfjsLib.GlobalWorkerOptions.workerSrc = require.resolve('pdfjs-dist/legacy/build/pdf.worker.js');
        this.LABEL_PATTERNS = {
            ID: /ת\.?ז\.?:?/i,
            NAME: /שם:?/i,
            DATE: /תאריך:?/i,
            AGE: /גיל:?/i,
            GENDER: /מגדר:?/i
        };
    }

    isRTLText(text) {
        if (!text) return false;
        // Hebrew and Arabic character ranges
        const rtlPattern = /[\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC]/;
        return rtlPattern.test(text);
    }

    classifyTextElement(text) {
        if (!text) return 'unknown';
        // Classify text elements based on patterns
        if (this.LABEL_PATTERNS.ID.test(text)) return 'id_field';
        if (this.LABEL_PATTERNS.NAME.test(text)) return 'name_field';
        if (this.LABEL_PATTERNS.DATE.test(text)) return 'date_field';
        if (this.LABEL_PATTERNS.AGE.test(text)) return 'age_field';
        if (this.LABEL_PATTERNS.GENDER.test(text)) return 'gender_field';
        
        // Additional classifications
        if (/^\d+$/.test(text)) return 'numeric';
        if (/^\d{1,2}[/.]\d{1,2}[/.]\d{4}$/.test(text)) return 'date';
        return 'general_text';
    }

    async readPDF(filePath) {
        try {
            const data = await fs.readFile(filePath);
            const pdf = await pdfjsLib.getDocument({
                data: new Uint8Array(data),
                useSystemFonts: true,
                standardFontDataUrl: `${__dirname}/node_modules/pdfjs-dist/standard_fonts/`
            }).promise;

            const structure = {
                pageCount: pdf.numPages,
                metadata: await pdf.getMetadata(),
                pages: [],
                formFields: {
                    detected: [],
                    potential: []
                },
                textGroups: []
            };

            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                const page = await pdf.getPage(pageNum);
                const pageStructure = await this.analyzePageEnhanced(page);
                structure.pages.push(pageStructure);
            }

            return structure;
        } catch (error) {
            console.error('Error reading PDF:', error);
            throw error;
        }
    }

    getTransformValues(item) {
        try {
            if (item.transform && Array.isArray(item.transform)) {
                return {
                    x: item.transform[4] || 0,
                    y: item.transform[5] || 0,
                    rotation: Math.atan2(item.transform[1] || 0, item.transform[0] || 1) * (180/Math.PI),
                    scale: Math.sqrt((item.transform[0] || 1) * (item.transform[0] || 1) + 
                                  (item.transform[1] || 0) * (item.transform[1] || 0))
                };
            }
        } catch (error) {
            console.warn('Transform extraction failed:', error);
        }

        return {
            x: 0,
            y: 0,
            rotation: 0,
            scale: 1
        };
    }

    async analyzePageEnhanced(page) {
        const pageStructure = {
            pageNumber: page.pageNumber,
            size: page.view,
            rotation: page.rotate || 0,
            textContent: [],
            contentAreas: []
        };

        try {
            const textContent = await page.getTextContent({ includeMarkedContent: true });
            
            pageStructure.textContent = textContent.items.map((item, index) => {
                const transform = this.getTransformValues(item);
                
                return {
                    id: `text_${page.pageNumber}_${index}`,
                    text: item.str || '',
                    position: {
                        x: transform.x,
                        y: transform.y,
                        width: item.width || 0,
                        height: item.height || 0,
                        rotation: transform.rotation
                    },
                    style: {
                        fontSize: transform.scale * 12,
                        fontName: item.fontName || 'unknown',
                        fontWeight: item.fontWeight || 'normal',
                        isRTL: this.isRTLText(item.str || '')
                    },
                    metadata: {
                        renderingOrder: index,
                        markedContent: item.markedContent || [],
                        type: this.classifyTextElement(item.str || '')
                    }
                };
            });

        } catch (error) {
            console.error('Error analyzing page:', error);
            pageStructure.error = error.message;
        }

        return pageStructure;
    }
}

// Example usage
async function main() {
    const reader = new EnhancedPDFReader();
    try {
        const structure = await reader.readPDF('pdf/sample_form.pdf');
        
        console.log('Enhanced Document Structure:');
        console.log('Total Pages:', structure.pageCount);
        console.log('Metadata:', JSON.stringify(structure.metadata, null, 2));
        
        for (const page of structure.pages) {
            console.log(`\nPage ${page.pageNumber}:`);
            if (page.error) {
                console.log('Page Error:', page.error);
                continue;
            }
            
            console.log('Text Elements:', page.textContent.length);
            
            // Log sample of text content
            console.log('\nSample Text Content:');
            page.textContent.slice(0, 5).forEach(item => {
                console.log(`- "${item.text}" (${item.metadata.type}) at (${item.position.x}, ${item.position.y})`);
                console.log(`  RTL: ${item.style.isRTL}, Font: ${item.style.fontName}`);
            });
        }
    } catch (error) {
        console.error('Failed to analyze PDF:', error);
    }
}

if (require.main === module) {
    main();
}

module.exports = EnhancedPDFReader;