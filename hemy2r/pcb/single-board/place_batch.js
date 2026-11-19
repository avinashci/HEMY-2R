const info = await eda.dmt_SelectControl.getCurrentDocumentInfo();
if (info.uuid!=='21900c4b8254a1a2') throw new Error('wrong page '+info.uuid);
const LIB='0819f05c4eef4c71ace90d822a990e87';
const all=[['R43','e7430550b99b4e31a5c885b865dde147'],['R44','be60f304bdf4486e908bd15535a43c6d'],['U15','c886f6e607f348fd854ee78453d084a8'],['C86','1fcffeacebec4bcab600894243e1bb8c'],['R45','b37953171ed04bc6822268db8e82ce1c'],['R46','7d526eeca0714686adc6896633c4a152'],['C88','8e2066dcddc04bbbaec8059659608eed'],['C89','a299e4f29fd2469688f76621c3d59c4d'],['D8','1b2a8e26cad842f09c3494125a973787'],['J10','4d018698282b47d4893c87aca1c32f67'],['Q1','79a17a80cabd40719b597fdc7a56f7bb'],['R47','4c1efea8e0884946a0b9422079d22f25'],['R48','4c1efea8e0884946a0b9422079d22f25'],['R49','4c1efea8e0884946a0b9422079d22f25'],['R50','2340647df7144fc5a30489ed06518eb5'],['D7','bf4406c5355f4651ab1d8904f4e23c9c']];
let comps = await eda.sch_PrimitiveComponent.getAll();
for (const c of comps){ if (c.getState_ComponentType()==='part' && /\?$/.test(c.getState_Designator()||'')){ const sid=c.getState_SupplierId(); const m=all.find(([d,u])=>u===c.getState_Component()?.uuid && !comps.some(x=>x.getState_Designator()===d)); if(m){ await eda.sch_PrimitiveComponent.modify(c.getState_PrimitiveId(),{designator:m[0]}); } } }
comps = await eda.sch_PrimitiveComponent.getAll();
const have = comps.map(c=>c.getState_Designator());
const out=[]; const t0=Date.now(); let n=have.length;
for (const [des,uuid] of all){ if (have.includes(des)) continue; if (Date.now()-t0>35000){ out.push('more'); break; }
  const x = 200 + (n%5)*150, y = 200 + Math.floor(n/5)*150; n++;
  const c = await eda.sch_PrimitiveComponent.create({libraryUuid:LIB, uuid}, x, y);
  if (!c) { out.push(des+':FAIL'); continue; }
  await eda.sch_PrimitiveComponent.modify(c.getState_PrimitiveId(), {designator: des});
  out.push(des+':'+(Date.now()-t0));
}
return out.join(' ')||'done';
