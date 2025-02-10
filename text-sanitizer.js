// text-sanitizer.js

// Common medical terms and measurements that should not be sanitized
const MEDICAL_TERMS = new Set([
    'CVA', 'FIM', 'MMSE', 'COPD', 'Diabetes', 'Mellitus',
    'עצמאי', 'בקבלה', 'בשחרור', 'אבחנות', 'פיזיותרפיה',
    'משקל', 'מטר', 'בציוני', 'אבח', 'יום', 'בברכה'
]);

class TextSanitizer {
    constructor() {
        this.nameMap = new Map();
        this.nameCounter = 1;
        
        this.patterns = {
            // ID patterns
            ID_NUMBER: /(?:ת\.?ז\.?|מספר\s*זהות\s*:?\s*)(\d{9})/g,
            STANDALONE_ID: /(?<!\d)\d{9}(?!\d|\s*\/)/g,
            
            // Name pattern
            NAME: /(ישראלי\s*ישראלי|(?:ד"ר|פרופ'|דר'|מר|גב'|בן|בת)\s+[א-ת]+(?:\s+[א-ת]+){0,2}|[א-ת]+\s+(?:כהן|לוי|ישראלי))/g,
            
            // File path pattern
            FILE_PATH: /(?:file:\/\/\/[^\s]*|discharge-letter\.html|\d+\/\d+\s*$)/g
        };
    }

    reset() {
        this.nameMap.clear();
        this.nameCounter = 1;
    }

    generateUniqueName() {
        return `PERSON_${String(this.nameCounter++).padStart(3, '0')}`;
    }

    shouldPreserveToken(token) {
        if (MEDICAL_TERMS.has(token.trim())) {
            return true;
        }
        
        // Preserve measurements and dates
        if (/^(?:\d+(?:\/\d+)?(?:\s*(?:מ"ג|מ״ג|ק"ג|ק״ג))?|\d{1,2}[\/\.]\d{1,2}[\/\.]\d{2,4})$/.test(token)) {
            return true;
        }

        return false;
    }

    sanitizeText(text) {
        if (!text || typeof text !== 'string') {
            return text;
        }

        // Remove file paths
        text = text.replace(this.patterns.FILE_PATH, '');

        // Replace ID numbers
        text = text.replace(this.patterns.ID_NUMBER, 'ת.ז.: ID_REDACTED');
        text = text.replace(this.patterns.STANDALONE_ID, 'ID_REDACTED');

        // Split text by existing spaces and process each token
        const words = text.split(/\s+/);
        const sanitizedWords = words.map(word => {
            // Skip empty words
            if (!word) return word;

            // Skip words that should be preserved
            if (this.shouldPreserveToken(word)) {
                return word;
            }

            // Handle names
            const nameMatch = word.match(this.patterns.NAME);
            if (nameMatch) {
                if (!this.nameMap.has(nameMatch[0])) {
                    this.nameMap.set(nameMatch[0], this.generateUniqueName());
                }
                return this.nameMap.get(nameMatch[0]);
            }

            return word;
        });

        // Join words back together with original spacing
        return sanitizedWords.join(' ');
    }

    sanitizeDocument(document) {
        this.reset();
        return {
            ...document,
            text: this.sanitizeText(document.text)
        };
    }
}

module.exports = TextSanitizer;