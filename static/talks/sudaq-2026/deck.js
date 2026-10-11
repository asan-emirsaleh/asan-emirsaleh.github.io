/* Sudaq lecture. All runtime dependencies and audio are local. */
Reveal.initialize({
  hash:true, controls:true, progress:true, slideNumber:'c/t',
  width:1280, height:720, margin:0.025, center:false,
  transition:'fade', backgroundTransition:'none', viewDistance:35,
  autoPlayMedia:false, pdfSeparateFragments:false
});
const notes = document.getElementById('speaker-notes');
const zoom = document.getElementById('figure-zoom');
function pauseAudio(reset=false) {
  document.querySelectorAll('audio').forEach(audio => {
    audio.pause();
    if(reset && audio.readyState > 0) audio.currentTime=0;
  });
}
function updateNotes() {
  const slide=Reveal.getCurrentSlide();
  const title=slide?.querySelector('h1')?.textContent || '';
  const number=Reveal.getIndices().h+1;
  document.getElementById('notes-title').textContent=`${number} / ${Reveal.getTotalSlides()} · ${title}`;
  document.getElementById('notes-body').innerHTML=slide?.querySelector('.notes')?.innerHTML || 'Нет заметок.';
}
Reveal.on('slidechanged', () => {pauseAudio(true); if(notes.open) updateNotes();});
document.addEventListener('play', event => {
  if(event.target.tagName!=='AUDIO') return;
  document.querySelectorAll('audio').forEach(audio=>{if(audio!==event.target) audio.pause();});
}, true);
document.addEventListener('keydown',event=>{
  if(event.key==='Escape' && (notes.open || zoom.open)) {
    event.preventDefault(); event.stopImmediatePropagation();
    if(zoom.open) zoom.close(); else notes.close();
    return;
  }
  if(event.key.toLowerCase()==='n' && !event.ctrlKey && !event.metaKey && !event.altKey && !/input|textarea/i.test(event.target.tagName)) {
    event.preventDefault(); event.stopImmediatePropagation();
    if(notes.open) notes.close(); else {updateNotes(); notes.showModal();}
  }
},true);
document.getElementById('close-notes').addEventListener('click',()=>notes.close());
document.getElementById('close-zoom').addEventListener('click',()=>zoom.close());
document.querySelectorAll('figure img').forEach(img=>{
  img.tabIndex=0;
  const enlarge=()=>{const target=document.getElementById('zoom-image');target.src=img.src;target.alt=img.alt;zoom.showModal();};
  img.addEventListener('click',enlarge);
  img.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();enlarge();}});
});
notes.addEventListener('close',()=>document.querySelector('.reveal').focus());
