/* AG-11 Video Background Handler - transición instantánea de splash a login */
document.addEventListener('DOMContentLoaded', function () {
  const splashContainer = document.getElementById('splash-container');
  const loginContainer = document.getElementById('login-container');
  const videoSplash = document.getElementById('background-video');
  const loginVideo = document.getElementById('login-video');

  if (!videoSplash || !loginContainer) return;

  // Precarga el video de login
  if (loginVideo) {
    loginVideo.load();
  }

  videoSplash.addEventListener('ended', function () {
    splashContainer.style.display = 'none';
    loginContainer.style.display = 'block';
    if (loginVideo) {
      loginVideo.currentTime = 0;
      const playPromise = loginVideo.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => { /* Silencia errores de autoplay */ });
      }
    }
  });
});
