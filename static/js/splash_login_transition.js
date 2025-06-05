/* AG-11 Video Background Handler - transición de splash a login */
window.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('splash-video');
  const loginContainer = document.getElementById('login-container');
  const splashLogo = document.getElementById('splash-logo');
  const splashText = document.getElementById('splash-text');
  let loginMostrado = false;

  if (!video || !loginContainer) return;

  video.ontimeupdate = function () {
    if (!loginMostrado && (video.duration - video.currentTime <= 1.5)) {
      loginContainer.style.display = 'block';
      if (splashLogo) splashLogo.style.display = 'none';
      if (splashText) splashText.style.display = 'none';
      video.pause();
      loginMostrado = true;
    }
  };
});
