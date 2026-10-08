/* Snow Day Forecaster embeddable widget loader.
   Paste on your page:  <div class="sdf-widget"></div>
                        <script src="https://www.snowdayforecaster.com/embed.js" async></script>
   It inserts the calculator and a visible credit link back to Snow Day Forecaster. */
(function(){
  var SITE="https://www.snowdayforecaster.com";
  function init(){
    var nodes=document.querySelectorAll(".sdf-widget:not([data-sdf-done])");
    nodes.forEach(function(el){
      el.setAttribute("data-sdf-done","1");
      var f=document.createElement("iframe");
      f.src=SITE+"/embed/";f.title="Snow Day Calculator";f.loading="lazy";
      f.setAttribute("scrolling","no");
      f.style.cssText="width:100%;max-width:440px;height:230px;border:1px solid #e2e8f0;border-radius:12px;background:#fff;display:block";
      el.appendChild(f);
      var cr=document.createElement("div");
      cr.style.cssText="max-width:440px;font:13px/1.4 system-ui,sans-serif;color:#64748b;margin:6px 0 0";
      cr.innerHTML='Snow day odds by <a href="'+SITE+'/" rel="noopener" style="color:#1d5bb8;font-weight:600">Snow Day Forecaster</a>';
      el.appendChild(cr);
    });
  }
  window.addEventListener("message",function(e){
    if(!e.data||e.data.sdf!==1)return;
    document.querySelectorAll(".sdf-widget iframe").forEach(function(f){
      if(f.contentWindow===e.source&&e.data.h){f.style.height=(e.data.h+2)+"px";}
    });
  });
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
