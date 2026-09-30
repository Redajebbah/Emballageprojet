// Emboitage — 3D hero: the three logo cubes as cardboard boxes (Three.js).
// Boxes drop in and snap into the logo arrangement, follow the pointer,
// lift on hover and drift apart while scrolling. Falls back to the SVG
// cubes already in the page if WebGL is unavailable.

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const container = document.querySelector('[data-hero-3d]');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (e) {
    return false;
  }
}

if (container && webglAvailable()) {
  try {
    init();
  } catch (err) {
    console.warn('Hero 3D disabled:', err);
  }
}

function init() {
  // ---------- Renderer / scene / camera ----------
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.domElement.className = 'hero-canvas';
  renderer.domElement.setAttribute('aria-hidden', 'true');
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(21, 1, 0.1, 100);
  camera.position.set(9.2, 7.4, 9.2);        // isometric-like view, as in the logo
  camera.lookAt(0, 0.1, 0);

  // ---------- Lights (top face brightest, right face darkest, like the logo) ----------
  scene.add(new THREE.HemisphereLight(0xfff6e6, 0x8b6f47, 1.55));
  const key = new THREE.DirectionalLight(0xffffff, 1.9);
  key.position.set(-3, 9, 6);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xffe2b0, 0.6);
  rim.position.set(6, 2, -6);
  scene.add(rim);

  // ---------- Cardboard grain texture (generated, no download) ----------
  const grain = makeCardboardTexture();

  // Face colors in BoxGeometry order: +x (right), -x, +y (top), -y, +z (left), -z
  const palette = [
    { right: 0x8b6f47, top: 0xe8cf99, left: 0xc9a66b },
    { right: 0x7d623e, top: 0xdfc289, left: 0xbe9960 },
    { right: 0x937650, top: 0xe8cf99, left: 0xcfae75 },
  ];
  const makeMaterials = (p) => [p.right, p.right, p.top, p.right, p.left, p.left].map((color) =>
    new THREE.MeshStandardMaterial({ color, roughness: 0.82, metalness: 0.0, map: grain, bumpMap: grain, bumpScale: 0.015 })
  );

  const boxGeo = new RoundedBoxGeometry(1, 1, 1, 5, 0.06);
  const tapeGeo = new THREE.BoxGeometry(0.24, 0.012, 1.004);
  const tapeMat = new THREE.MeshStandardMaterial({ color: 0xf1e4c8, roughness: 0.35, transparent: true, opacity: 0.92 });

  // Logo arrangement (derived from the isometric logo): top cube, lower-left, lower-right.
  const layout = [
    new THREE.Vector3(0, 0.25, 0),
    new THREE.Vector3(0, -0.25, 1.0),
    new THREE.Vector3(1.0, -0.25, 0),
  ];
  const center = new THREE.Vector3(0.33, 0, 0.33);

  const group = new THREE.Group();
  scene.add(group);

  const cubes = layout.map((pos, i) => {
    const pivot = new THREE.Group();
    const mesh = new THREE.Mesh(boxGeo, makeMaterials(palette[i]));
    const tape = new THREE.Mesh(tapeGeo, tapeMat);
    tape.position.y = 0.5 + 0.004;
    tape.rotation.y = i === 1 ? Math.PI / 2 : 0;
    pivot.add(mesh, tape);
    pivot.userData = {
      home: pos.clone().sub(center),
      delay: 0.15 + i * 0.18,
      phase: i * 2.1,
      lift: 0,
      spin: (i % 2 ? -1 : 1) * (0.9 + i * 0.35),
    };
    mesh.userData.pivot = pivot;
    group.add(pivot);
    return pivot;
  });

  // ---------- Soft contact shadow ----------
  const shadow = new THREE.Mesh(
    new THREE.PlaneGeometry(4.2, 4.2),
    new THREE.MeshBasicMaterial({ map: makeShadowTexture(), transparent: true, depthWrite: false, opacity: 0.55 })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = -1.15;
  scene.add(shadow);

  // ---------- Floating small boxes ----------
  const particleCount = window.innerWidth < 768 ? 16 : 28;
  const particles = new THREE.InstancedMesh(
    new RoundedBoxGeometry(1, 1, 1, 2, 0.12),
    new THREE.MeshStandardMaterial({ color: 0xd4b896, roughness: 0.7, transparent: true, opacity: 0.85 }),
    particleCount
  );
  const pData = Array.from({ length: particleCount }, () => ({
    pos: new THREE.Vector3((Math.random() - 0.5) * 7, (Math.random() - 0.5) * 5, (Math.random() - 0.5) * 7),
    rot: new THREE.Euler(Math.random() * 6, Math.random() * 6, 0),
    speed: 0.08 + Math.random() * 0.18,
    spin: (Math.random() - 0.5) * 0.8,
    size: 0.05 + Math.random() * 0.1,
  }));
  const tints = [0xd4b896, 0xc9a66b, 0xeadbc0, 0x8b6f47];
  pData.forEach((_, i) => particles.setColorAt(i, new THREE.Color(tints[i % tints.length])));
  scene.add(particles);
  const dummy = new THREE.Object3D();

  // ---------- Interaction state ----------
  const pointer = new THREE.Vector2(0, 0);      // -1..1, for parallax
  const pointerNdc = new THREE.Vector2(9, 9);   // for hover raycast
  const raycaster = new THREE.Raycaster();
  let hovered = null;
  let scrollProgress = 0;

  window.addEventListener('pointermove', (e) => {
    pointer.set((e.clientX / window.innerWidth) * 2 - 1, (e.clientY / window.innerHeight) * 2 - 1);
    const r = renderer.domElement.getBoundingClientRect();
    pointerNdc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  }, { passive: true });
  renderer.domElement.addEventListener('pointerleave', () => pointerNdc.set(9, 9));

  // Boxes drift apart as the 3D block itself scrolls out of view (works on mobile,
  // where the visual sits below the text).
  const onScroll = () => {
    const r = container.getBoundingClientRect();
    const start = window.innerHeight * 0.15;
    scrollProgress = Math.min(Math.max((start - r.top) / (r.height || 1), 0), 1);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---------- Size ----------
  function resize() {
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container);
  resize();

  // ---------- Animation ----------
  const easeOutBack = (t) => { const c1 = 1.55, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
  const clock = new THREE.Clock();
  const tilt = new THREE.Vector2();
  let lastTime = 0;

  function frame() {
    const now = clock.getElapsedTime();
    const dt = Math.min(now - lastTime, 0.05);
    lastTime = now;
    const t = reduceMotion ? 10 : now;

    // Hover detection
    raycaster.setFromCamera(pointerNdc, camera);
    const hit = raycaster.intersectObjects(cubes.map((c) => c.children[0]), false)[0];
    hovered = hit ? hit.object.userData.pivot : null;
    renderer.domElement.style.cursor = hovered ? 'pointer' : '';

    // Cubes: intro drop, idle bob, hover lift, scroll spread
    cubes.forEach((c) => {
      const d = c.userData;
      const k = Math.min(Math.max((t - d.delay) / 1.1, 0), 1);
      const intro = easeOutBack(k);
      d.lift += ((hovered === c ? 0.28 : 0) - d.lift) * 0.12;
      const bob = reduceMotion ? 0 : Math.sin(t * 1.2 + d.phase) * 0.05;
      const spread = 1 + scrollProgress * 0.9;

      c.position.set(
        d.home.x * spread,
        d.home.y * spread + (1 - intro) * 5 + bob + d.lift,
        d.home.z * spread
      );
      c.rotation.y = (1 - intro) * d.spin + scrollProgress * d.spin * 0.6;
      c.rotation.x = (1 - intro) * 0.6 + scrollProgress * 0.35 * d.spin;
      c.scale.setScalar(0.6 + 0.4 * Math.min(k * 1.6, 1));
    });

    // Whole group: slow sway + pointer parallax
    tilt.x += (pointer.y * 0.18 - tilt.x) * 0.05;
    tilt.y += (pointer.x * 0.35 - tilt.y) * 0.05;
    group.rotation.x = tilt.x;
    group.rotation.y = tilt.y + (reduceMotion ? 0 : Math.sin(t * 0.35) * 0.18);
    group.position.y = -scrollProgress * 0.6;

    // Shadow follows the intro and the spread
    const settled = Math.min(Math.max((t - 0.2) / 1.4, 0), 1);
    shadow.material.opacity = 0.55 * settled * (1 - scrollProgress * 0.6);
    shadow.scale.setScalar(0.7 + 0.3 * settled + scrollProgress * 0.5);

    // Floating boxes drift upward and wrap around
    pData.forEach((p, i) => {
      if (!reduceMotion) {
        p.pos.y += p.speed * dt;
        if (p.pos.y > 2.8) p.pos.y = -2.8;
        p.rot.x += p.spin * dt;
        p.rot.y += p.spin * dt * 0.7;
      }
      dummy.position.copy(p.pos);
      dummy.rotation.copy(p.rot);
      dummy.scale.setScalar(p.size);
      dummy.updateMatrix();
      particles.setMatrixAt(i, dummy.matrix);
    });
    particles.instanceMatrix.needsUpdate = true;
    particles.rotation.y = tilt.y * 0.5;

    renderer.render(scene, camera);
  }

  // Only render while the hero is on screen
  let running = false;
  const start = () => { if (!running) { running = true; renderer.setAnimationLoop(frame); } };
  const stop = () => { if (running) { running = false; renderer.setAnimationLoop(null); } };
  new IntersectionObserver(([entry]) => (entry.isIntersecting ? start() : stop()), { threshold: 0 }).observe(container);
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));

  frame();
  container.classList.add('is-3d');
}

// Fine cardboard grain + faint flute lines, generated on a canvas.
function makeCardboardTexture() {
  const size = 256;
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, size, size);
  const img = ctx.getImageData(0, 0, size, size);
  for (let i = 0; i < img.data.length; i += 4) {
    const n = 232 + Math.random() * 23;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = n;
  }
  ctx.putImageData(img, 0, 0);
  ctx.globalAlpha = 0.06;
  ctx.fillStyle = '#000';
  for (let y = 0; y < size; y += 6) ctx.fillRect(0, y, size, 2);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  return tex;
}

function makeShadowTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, 'rgba(58,44,32,0.55)');
  g.addColorStop(0.45, 'rgba(58,44,32,0.22)');
  g.addColorStop(1, 'rgba(58,44,32,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
}
