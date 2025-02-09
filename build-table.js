const Papa = require('papaparse');
const _ = require('lodash');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

const FIELD_TYPES = {
    string: 'string',
    integer: 'number',
    boolean: 'boolean'
};

const REQUIRED_FIELDS = [
    { name: 'patient_id', type: FIELD_TYPES.string },
    { name: 'name', type: FIELD_TYPES.string },
    { name: 'admission_date', type: FIELD_TYPES.string },
    { name: 'discharge_date', type: FIELD_TYPES.string },
    { name: 'gender', type: FIELD_TYPES.string },
    { name: 'age_at_admission', type: FIELD_TYPES.integer },
    { name: 'holocaust_survivor', type: FIELD_TYPES.string },
    { name: 'living_arrangement', type: FIELD_TYPES.string },
    { name: 'residence_type', type: FIELD_TYPES.string },
    { name: 'floor_number', type: FIELD_TYPES.integer },
    { name: 'elevator', type: FIELD_TYPES.string },
    { name: 'stairs_count', type: FIELD_TYPES.string },
    { name: 'education_years', type: FIELD_TYPES.string },
    { name: 'admission_reason', type: FIELD_TYPES.string },
    { name: 'admission_source', type: FIELD_TYPES.string },
    { name: 'physical_examination', type: FIELD_TYPES.string },
    { name: 'medications_type', type: FIELD_TYPES.string },
    { name: 'allergies', type: FIELD_TYPES.string },
    { name: 'tests', type: FIELD_TYPES.string },
    { name: 'past_procedures', type: FIELD_TYPES.string },
    { name: 'mobility', type: FIELD_TYPES.string },
    { name: 'transfers', type: FIELD_TYPES.string },
    { name: 'dressing', type: FIELD_TYPES.string },
    { name: 'bathing', type: FIELD_TYPES.string },
    { name: 'eating_status', type: FIELD_TYPES.string },
    { name: 'continence', type: FIELD_TYPES.string },
    { name: 'cognitive_status', type: FIELD_TYPES.string },
    { name: 'mmse_score', type: FIELD_TYPES.integer },
    { name: 'cognitive_assessment', type: FIELD_TYPES.string },
    { name: 'consciousness', type: FIELD_TYPES.string },
    { name: 'mood', type: FIELD_TYPES.string },
    { name: 'anxiety', type: FIELD_TYPES.string },
    { name: 'pain_level', type: FIELD_TYPES.string },
    { name: 'sleep_issues', type: FIELD_TYPES.string },
    { name: 'constipation', type: FIELD_TYPES.string },
    { name: 'handedness', type: FIELD_TYPES.string },
    { name: 'sensation', type: FIELD_TYPES.string },
    { name: 'gross_strength', type: FIELD_TYPES.string },
    { name: 'language_communication', type: FIELD_TYPES.string },
    { name: 'nursing_care_claim', type: FIELD_TYPES.string },
    { name: 'hospitalization_extension', type: FIELD_TYPES.string },
    { name: 'discharge_destination', type: FIELD_TYPES.string },
    { name: 'rehabilitation_type', type: FIELD_TYPES.string },
    { name: 'aid_law', type: FIELD_TYPES.string },
    { name: 'fim_score', type: FIELD_TYPES.string },
    { name: 'diagnoses', type: FIELD_TYPES.string }
];

async function generatePrompt(text, parameters) {
    const hebrewInstructions = `נתח את הטקסט הרפואי הבא והוצא את המידע הבא בפורמט JSON.
עבור כל שדה, השתמש אך ורק באפשרויות המצוינות או 'not_found' אם המידע חסר.

אפשרויות לכל שדה:
`;
    
    const fieldOptions = parameters.map(param => 
        `${param.field}: [${param.possible_values.split('|').join(', ')}]`
    ).join('\n');

    return `${hebrewInstructions}
${fieldOptions}

הטקסט הרפואי:
${text}

יש להחזיר JSON תקין בפורמט הבא:
{
    ${REQUIRED_FIELDS.map(field => `"${field.name}": ${field.type}`).join(',\n    ')}
}`;
}

async function analyzeMedicalTextWithLLM(text, parameters) {
    try {
        //const prompt = await generatePrompt(text, parameters);
        const prompt = "איך להכין עוגה?";
        const response = await axios.post('http://localhost:8000/query', {
            text: prompt
        });
        //console.log('llm response:',response.data.response.choices[0].text)
        const llmResponse = response.data.response.choices[0].text;
        try {
            const md = JSON.parse(llmResponse);
            console.log('structured llm response:',md)
            return md;
        } catch (e) {
            console.error('Failed to parse LLM response:', llmResponse);
            return createEmptyRecord();
        }
    } catch (error) {
        console.error('LLM API error:', error.message);
        return createEmptyRecord();
    }
}

function createEmptyRecord() {
    return REQUIRED_FIELDS.reduce((acc, field) => {
        acc[field.name] = 'not_found';
        return acc;
    }, {});
}

function validateRecord(record, parameters) {
    REQUIRED_FIELDS.forEach(field => {
        const param = parameters.find(p => p.field === field.name);
        if (!param) return;

        const validValues = param.possible_values.split('|');
        if (!validValues.includes(record[field.name])) {
            record[field.name] = 'not_found';
        }

        if (field.type === FIELD_TYPES.integer) {
            const num = parseInt(record[field.name]);
            if (isNaN(num)) {
                record[field.name] = 'not_found';
            } else {
                record[field.name] = num;
            }
        }
    });
    return record;
}

async function processPatientData(inputDir = 'results') {
    try {
        const paramsText = fs.readFileSync('parameters.csv', 'utf8');
        const parameters = Papa.parse(paramsText, { header: true, skipEmptyLines: true }).data;

        const searchResults = fs.readFileSync(path.join(inputDir, 'searchable_text.csv'), 'utf8');
        const results = Papa.parse(searchResults, { header: true, skipEmptyLines: true }).data;
        const patientGroups = _.groupBy(results, 'filename');
        
        const patientData = await Promise.all(
            Object.entries(patientGroups).map(async ([filename, pages]) => {
                const fullText = pages.map(page => page['Text Content']).join(' ');
                const record = await analyzeMedicalTextWithLLM(fullText, parameters);
                return validateRecord(record, parameters);
            })
        );

        const csv = Papa.unparse(patientData);
        fs.writeFileSync('patient_data.csv', csv);
        console.log(`Processed ${patientData.length} patient records`);
        return patientData;
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    const inputDir = process.argv[2] || 'results';
    processPatientData(inputDir);
}

module.exports = processPatientData;