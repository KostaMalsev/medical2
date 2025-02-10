// text-sanitizer.js
const fs = require('fs');
const path = require('path');

// Expanded medical terms and common words that should not be sanitized
const PRESERVED_TERMS = new Set([
    // Medical conditions and tests
    'CVA', 'FIM', 'MMSE', 'COPD', 'Diabetes', 'Mellitus',
    
    // Common medical terms in Hebrew
    'עצמאי', 'בקבלה', 'בשחרור', 'אבחנות', 'פיזיותרפיה',
    'משקל', 'מטר', 'בציוני', 'אבח', 'יום', 'בברכה',
    
    // Medical document terms
    'מחלקת', 'שיקום', 'מכתב', 'שחרור', 'תאריך', 'קבלה',
    'תיק', 'רפואי', 'לידה', 'עיקריות', 'איסכמי', 'המיספרה',
    'שמאלית', 'לחץ', 'דם', 'סוכרת', 'מסוג', 'הערכת',
    'מוטורי', 'טיפול', 'עצמי', 'רחצה', 'הלבשה', 'גוף',
    'עליון', 'תחתון', 'בסוגרים', 'שתן', 'צואה',
    
    // Medical activities and measurements
    'העברות', 'מיטה', 'כסא', 'שירותים', 'אמבטיה', 'מקלחת',
    'ניידות', 'מדרגות', 'קוגניטיבי', 'הבנה', 'הבעה',
    'אינטראקציה', 'חברתית', 'פתרון', 'בעיות', 'זיכרון',
    
    // Common words and phrases
    'החולים', 'הכללי', 'בית', 'מספר', 'סיכום', 'מהלך',
    'האשפוז', 'המטופל', 'התקבל', 'למחלקת', 'לאחר', 'אירוע',
    'מוחי', 'בקבלתו', 'סבל', 'מחולשה', 'בפלג', 'קשיים',
    'בדיבור', 'והפרעה', 'בשיווי', 'במהלך', 'עבר', 'שיקומי',
    'אינטנסיבי', 'הכולל', 'ריפוי', 'בעיסוק', 'קלינאות',
    'תקשורת', 'מסוגל', 'כעת', 'לבצע', 'חל', 'שיפור',
    'משמעותי', 'בתפקוד', 'המוטורי', 'והקוגניטיבי', 'כפי',
    'שמשתקף', 'מרבית', 'פעולות', 'היומיום', 'באופן',
    'בעזרה', 'מינימלית', 'הליכה', 'מתבצעת', 'בעזרת',
    'הליכון', 'לטווח', 'המלצות', 'המשך', 'במסגרת', 'מעקב',
    'משפחה', 'תרופתי', 'פעם', 'פעמיים', 'בשבוע'
]);

class TextSanitizer {
    constructor(namesFilePath = 'hebrew_names.csv') {
        this.idCounter = 1;
        this.namesSet = new Set();
        
        // Load names from CSV
        try {
            const namesList = fs.readFileSync(namesFilePath, 'utf8')
                              .split('\n')
                              .map(name => name.trim())
                              .filter(name => name.length > 0);
            this.namesSet = new Set(namesList);
            console.log(`Loaded ${this.namesSet.size} names from ${namesFilePath}`);
        } catch (error) {
            console.error(`Error loading names from ${namesFilePath}:`, error.message);
        }
        
        this.patterns = {
            ID_NUMBER: /(?:ת\.?ז\.?|מספר\s*זהות\s*:?\s*)(\d{9})/g,
            STANDALONE_ID: /(?<!\d)\d{9}(?!\d|\s*\/)/g,
            NAME_PREFIX: /(?:ד"ר|פרופ'|דר'|מר|גב'|בן|בת)\s+/,
            FILE_PATH: /(?:file:\/\/\/[^\s]*|discharge-letter\.html|\d+\/\d+\s*$)/g,
            EXTRA_SPACES: /(?<=[א-ת])\s+(?=[א-ת])/g,
            MULTIPLE_SPACES: /\s{2,}/g
        };
    }

    reset() {
        this.idCounter = 1;
    }

    generateUniqueId() {
        return `ID_${String(this.idCounter++).padStart(6, '0')}`;
    }

    generateRedactedName() {
        return '"ףף"';
    }

    shouldPreserveToken(token) {
        const cleanToken = token.trim();
        
        if (PRESERVED_TERMS.has(cleanToken)) {
            return true;
        }
        
        if (/^(?:\d+(?:\/\d+)?(?:\s*(?:מ"ג|מ״ג|ק"ג|ק״ג))?|\d{1,2}[\/\.]\d{1,2}[\/\.]\d{2,4})$/.test(cleanToken)) {
            return true;
        }

        if (/^[א-ת]{1,2}$/.test(cleanToken)) {
            return true;
        }

        return false;
    }

    isName(word) {
        if (word.length < 2) return false;
        
        const cleanWord = word.replace(this.patterns.NAME_PREFIX, '').trim();
        
        return this.namesSet.has(cleanWord) || 
               /(?:ישראלי|כהן|לוי)$/.test(cleanWord);
    }

    normalizeSpaces(text) {
        // Join incorrectly split Hebrew words
        let words = text.split(/\s+/);
        let result = [];
        let currentWord = '';
        
        for (let i = 0; i < words.length; i++) {
            let word = words[i];
            
            // Handle Hebrew characters
            if (/^[א-ת]$/.test(word) && currentWord !== '') {
                currentWord += word;
            }
            // Handle multi-character Hebrew words
            else if (/^[א-ת]{2,}$/.test(word)) {
                if (currentWord !== '') {
                    result.push(currentWord);
                }
                currentWord = word;
            }
            // Handle non-Hebrew or mixed content
            else {
                if (currentWord !== '') {
                    result.push(currentWord);
                    currentWord = '';
                }
                result.push(word);
            }
        }
        
        // Add any remaining word
        if (currentWord !== '') {
            result.push(currentWord);
        }
        
        return result.join(' ');
    }

    sanitizeText(text) {
        if (!text || typeof text !== 'string') {
            return text;
        }

        // Remove file paths first
        text = text.replace(this.patterns.FILE_PATH, '');

        // Replace IDs with unique IDs
        text = text.replace(this.patterns.ID_NUMBER, (match) => {
            const uniqueId = this.generateUniqueId();
            return `ת.ז.: ${uniqueId}`;
        });
        text = text.replace(this.patterns.STANDALONE_ID, () => this.generateUniqueId());

        // Normalize spaces and split into words
        text = this.normalizeSpaces(text);
        const words = text.split(/\s+/);
        let sanitizedWords = [];
        
        for (let i = 0; i < words.length; i++) {
            let word = words[i];
            
            if (!word) continue;

            // Preserve medical terms and common words
            if (this.shouldPreserveToken(word)) {
                sanitizedWords.push(word);
                continue;
            }

            // Handle names
            if (this.isName(word)) {
                let fullName = word;
                let j = i + 1;
                while (j < words.length && this.isName(words[j])) {
                    fullName += ' ' + words[j];
                    j++;
                }
                
                sanitizedWords.push(this.generateRedactedName());
                i = j - 1;
                continue;
            }

            sanitizedWords.push(word);
        }

        // Join words and clean up spacing
        return sanitizedWords.join(' ')
            .replace(this.patterns.MULTIPLE_SPACES, ' ')
            .trim();
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