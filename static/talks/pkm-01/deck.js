Reveal.initialize({hash:true,controls:true,progress:true,slideNumber:'c/t',width:1280,height:720,margin:0.025,center:false,transition:'fade',backgroundTransition:'none',viewDistance:35,pdfSeparateFragments:false});
const zoom=document.getElementById('figure-zoom');
document.getElementById('close-zoom').addEventListener('click',()=>zoom.close());
document.querySelectorAll('figure img').forEach(img=>{
  const enlarge=()=>{const target=document.getElementById('zoom-image');target.src=img.src;target.alt=img.alt;zoom.showModal();};
  img.addEventListener('click',enlarge);
  img.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();enlarge();}});
});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&zoom.open){event.preventDefault();event.stopImmediatePropagation();zoom.close();}},true);
