/* AG-11 Video Background Handler */
document.addEventListener('DOMContentLoaded', function () {
  const videos = [
    document.getElementById('background-video'),
    document.getElementById('login-video'),
  ].filter(Boolean);
  if (!videos.length) return;

  const preloader = document.getElementById('preloader');

  function setupVideo(video, startBtn) {
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
  }

  videos.forEach((v) => {
    const startBtn = v.id === 'background-video'
      ? document.getElementById('start-experience')
      : document.getElementById('start-login');
    setupVideo(v, startBtn);
  });
});
