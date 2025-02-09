const Papa = require('papaparse');
const _ = require('lodash');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

async function loadParameters() {
    const paramsText = fs.readFileSync('transformed_parameters.csv', 'utf8');
    return Papa.parse(paramsText, {
        header: true,
        skipEmptyLines: true
    }).data;
}

function getFieldValues(row) {
    return _.compact([
        row['Value 1'], row['Value 2'], row['Value 3'], 
        row['Value 4'], row['Value 5'], row['Value 6'],
        row['Value 7'], row['Value 8'], row['Value 9'], 
        row['Value 10'], row['Value 11']
    ]);
}

function validateFieldValue(value, possibleValues) {
    return value || value === 'not_found' ? value : 'not_found';
}

async function analyzeMedicalTextWithNER(text, parameters) {
    try {
        const response = await axios.post('http://localhost:8000/query', {
            text,
            parameters: parameters.map(p => ({
                field: p.Field,
                options: getFieldValues(p)
            }))
        });
        return mapNERtoFields(response.data.response, parameters);
    } catch (error) {
        console.error('NER API error:', error.message);
        return createEmptyRecord(parameters);
    }
}

function mapNERtoFields(entities, parameters) {
    const record = createEmptyRecord(parameters);
    
    parameters.forEach(param => {
        if (entities[param.Field]) {
            record[param.Field] = validateFieldValue(
                entities[param.Field],
                getFieldValues(param)
            );
        }
    });
    
    return record;
}

function createEmptyRecord(parameters) {
    return parameters.reduce((acc, param) => {
        acc[param.Field] = 'not_found';
        return acc;
    }, {});
}

async function processPatientData(inputDir = 'results') {
    try {
        const parameters = await loadParameters();
        const searchResults = fs.readFileSync(path.join(inputDir, 'searchable_text.csv'), 'utf8');
        const results = Papa.parse(searchResults, {
            header: true,
            skipEmptyLines: true
        }).data;
        
        const patientGroups = _.groupBy(results, 'filename');
        
        const patientData = await Promise.all(
            Object.entries(patientGroups).map(async ([filename, pages]) => {
                const fullText = pages.map(page => page['Text Content']).join(' ');
                const res = await analyzeMedicalTextWithNER(fullText, parameters);
                console.table(res)
                return res;
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