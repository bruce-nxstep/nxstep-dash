const pptxgen = require('pptxgenjs');
const html2pptx = require('./scripts/html2pptx');
const path = require('path');

async function createPresentation() {
    console.log("Starting PPTX Generation...");

    // Create new Presentation
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'NXSTEP';
    pptx.title = 'NXSTEP Business Proposal';

    // List of slides
    const slides = [
        'slides/slide1.html',
        'slides/slide2.html',
        'slides/slide3.html',
        'slides/slide4.html',
        'slides/slide5.html',
        'slides/slide6.html',
        'slides/slide7.html',
    ];

    for (let i = 0; i < slides.length; i++) {
        const slidePath = slides[i];
        console.log(`Processing ${slidePath}...`);

        try {
            // We pass the full path relative to CWD
            const fullPath = path.join(__dirname, slidePath);
            await html2pptx(fullPath, pptx);
        } catch (err) {
            console.error(`Error processing ${slidePath}:`, err);
            require('fs').writeFileSync('error_log.txt', `Error processing ${slidePath}: ${err.stack}\n`, { flag: 'a' });
        }
    }

    // Save
    const outputFile = 'NXSTEP_Business_Proposal_Modern.pptx';
    console.log(`Saving to ${outputFile}...`);
    await pptx.writeFile({ fileName: outputFile });
    console.log('Presentation created successfully!');
}

createPresentation().catch(err => {
    console.error("Fatal Error:", err);
    process.exit(1);
});
