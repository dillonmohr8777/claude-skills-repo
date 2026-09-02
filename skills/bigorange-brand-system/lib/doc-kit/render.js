// node render.js in.html out.pdf "Footer label"
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path');
const {PDFDocument,rgb}=require('pdf-lib'); const fontkit=require('@pdf-lib/fontkit');
(async()=>{
  const [,, inFile, outFile, label]=process.argv;
  const b=await chromium.launch(); const p=await b.newPage();
  await p.goto('file://'+path.resolve(inFile),{waitUntil:'networkidle'}); await p.evaluate(()=>document.fonts.ready);
  await p.addStyleTag({content:'.body-only{display:none!important}'});
  const cover=await p.pdf({preferCSSPageSize:true,printBackground:true});
  await p.addStyleTag({content:'.body-only{display:block!important}.cover-only{display:none!important} @page{size:Letter;margin:0.85in 0.85in 1.05in 0.85in}'});
  const body=await p.pdf({preferCSSPageSize:true,printBackground:true});
  await b.close();
  const out=await PDFDocument.create(); out.registerFontkit(fontkit);
  const font=await out.embedFont(fs.readFileSync('assets/Montserrat[wght].ttf'),{subset:true});
  for (const buf of [cover,body]){const d=await PDFDocument.load(buf); const pg=await out.copyPages(d,d.getPageIndices()); pg.forEach(x=>out.addPage(x));}
  const pages=out.getPages(); const orange=rgb(1,0.486,0), mute=rgb(0.43,0.416,0.4), ink=rgb(0.07,0.07,0.07);
  pages.forEach((pg,i)=>{ if(i===0) return; const {width}=pg.getSize(); const y=0.55*72; const size=6.4;
    pg.drawText(label.toUpperCase(),{x:0.85*72,y,size,font,color:mute});
    const n=String(i); const nw=font.widthOfTextAtSize(n,7.2);
    pg.drawRectangle({x:width-0.85*72-nw-9,y:y-0.5,width:5,height:5,color:orange});
    pg.drawText(n,{x:width-0.85*72-nw,y,size:7.2,font,color:ink});
  });
  out.setTitle(label); out.setAuthor('BigOrange.Marketing'); out.setProducer('BigOrange.Marketing');
  fs.writeFileSync(outFile,await out.save()); console.log('wrote',outFile,pages.length,'pages');
})().catch(e=>{console.error(e);process.exit(1)});
