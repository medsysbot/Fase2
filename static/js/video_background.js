/* AG-11 Video Background Handler */
document.addEventListener('DOMContentLoaded', function () {
  const video = document.getElementById('background-video');
  if (!video) return;
  const preloader = document.getElementById('preloader');
  const startBtn = document.getElementById('start-experience');

  function showContent() {
    document.body.classList.add('ready');
    if (preloader) {
      preloader.style.display = 'none';
    }
  }

  video.addEventListener('canplaythrough', showContent);

  const playPromise = video.play();
  if (playPromise !== undefined) {
    playPromise.then(showContent).catch(() => {
      if (startBtn) {
        startBtn.style.display = 'block';
      }
    });
  }

  if (startBtn) {
    startBtn.addEventListener('click', () => {
      video.muted = false;
      video.play();
      startBtn.style.display = 'none';
      showContent();
    });
  }
});
