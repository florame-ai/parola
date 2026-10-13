/* Cache is scoped to this repository, never to other GitHub Pages apps. */
const PREFIX='parola-v6:'+new URL(self.registration.scope).pathname+':';
const CACHE=PREFIX+'6.0.0';
const SHELL=['./','./index.html','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL))));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 for(const key of await caches.keys())if(key.startsWith(PREFIX)&&key!==CACHE)await caches.delete(key);
 await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url),scope=new URL(self.registration.scope);
 if(request.method!=='GET'||url.origin!==scope.origin||!url.pathname.startsWith(scope.pathname)||request.headers.has('range'))return;
 if(request.mode==='navigate'){
  event.respondWith((async()=>{
   try{const response=await fetch(request);if(response.ok){const cache=await caches.open(CACHE);await cache.put('./index.html',response.clone());return response;}throw Error('Offline response');}
   catch{return await caches.match(new URL('./index.html',self.registration.scope).href)||Response.error();}
  })());
 }else{
  event.respondWith((async()=>{
   const cached=await caches.match(request);if(cached)return cached;
   const response=await fetch(request);
   if(response.ok&&(url.pathname.includes('/audio/')||SHELL.some(path=>new URL(path,self.registration.scope).pathname===url.pathname))){const cache=await caches.open(CACHE);await cache.put(request,response.clone());}
   return response;
  })());
 }
});
