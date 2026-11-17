// Interactive 3D "Kyle" for the hero section.
// Model: model/kyle_rigged.glb (built by blender/build_kyle_v2.py) — skinned, with
// animation clips Idle, Wave, Happy, Thinking, Goodbye, Turn and face morph targets.
//
// Interactions
//   • page load → he waves hello;  hover him → he waves again
//   • click/tap or Enter/Space → happy bounce + "hehe"
//   • head follows the cursor anywhere on the page
//   • leave him alone for a while → he starts thinking; move the mouse → back to idle
//   • cursor leaves the window → goodbye wave
//   • move the cursor around → curious face: eyes open and follow it, a brow lifts,
//     a little "oh" on fast flicks; stop moving → back to his happy grin
//   • drag sideways → spin him (springs back)
//   • scrolling → he bounces with the scroll speed
// Shows the static portrait only if WebGL or the model is unavailable.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const stageEl = document.getElementById('kyleStage');
const canvas = document.getElementById('kyleCanvas');

if (stageEl && canvas && hasWebGL()) init();
else if (stageEl) showPortrait();

function showPortrait() {
    const img = document.createElement('img');
    img.src = 'img/profile-dark.png';
    img.alt = 'Portrait of Kyle Anthony Magalona';
    img.className = 'kyle-fallback';
    stageEl.prepend(img);
    canvas?.remove();
    stageEl.querySelector('.kyle-hint')?.remove();
}

function hasWebGL() {
    try {
        const c = document.createElement('canvas');
        return !!(c.getContext('webgl2') || c.getContext('webgl'));
    } catch { return false; }
}

function init() {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ------------------------------------------------------------------ renderer
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;    // punchier than AgX for a toy-like look
    renderer.toneMappingExposure = 1.0;

    const scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    const camera = new THREE.PerspectiveCamera(24, 4 / 5, 0.05, 30);

    // soft three-point setup (matches the Blender presentation renders)
    const hemi = new THREE.HemisphereLight(0xffffff, 0x8a8299, 0.45);
    const key = new THREE.DirectionalLight(0xfff1e4, 2.6);
    key.position.set(-1.6, 2.2, 2.4);
    const fill = new THREE.DirectionalLight(0xe6eeff, 0.6);
    fill.position.set(2.2, 0.8, 1.8);
    const rim = new THREE.DirectionalLight(0xb9caff, 1.2);
    rim.position.set(0.8, 2.0, -2.2);
    // spotlight from straight above: lights the hair and shoulders like a stage light
    const top = new THREE.SpotLight(0xfff3e0, 5, 0, 0.42, 0.85, 2);
    top.position.set(0, 2.3, 0.35);
    top.target.position.set(0, 0.45, 0);
    scene.add(hemi, key, fill, rim, top, top.target);

    // the site is dark-only: dim ambient, strong cool rim to separate him from the background
    scene.environmentIntensity = 0.22;
    hemi.intensity = 0.35;
    rim.intensity = 2.6;

    // ------------------------------------------------------------------ state
    const stage = new THREE.Group();          // pivot at the feet: spin/hop/lean
    scene.add(stage);
    const lookTarget = new THREE.Vector3(0, 0.5, 0);
    const hitBox = new THREE.Box3();

    const pointer = { x: 0, y: 0, has: false };
    const look = { yaw: 0, pitch: 0, vy: 0, vp: 0 };
    const headAnchor = new THREE.Vector3(0, 0.8, 0);
    let ready = false;
    let mixer = null;
    const actions = {};
    let current = null;       // name of the playing clip
    let bones = {};
    let hovering = false;
    let hoverSince = 0;       // when the cursor started resting on him
    let hoverWaved = false;
    let hopY = 0, hopV = 0;   // spring for bounces
    let dragYaw = 0, dragVel = 0, dragging = false, dragStartX = 0, dragMoved = 0, lastDragX = 0;
    let scrollVel = 0, lastScroll = window.scrollY;
    let lastInput = performance.now();
    let lastOneShot = 0;
    let faceMeshes = [];      // GEO_Face primitives (all share the same morph targets)
    const eyes = [];          // eye bones: nudged toward the cursor while the eyes are open
    const mood = { curious: 0, happy: 0, oh: 0 };
    let pointerSpeed = 0, lastMoveT = -1e9, lastPX = 0, lastPY = 0;
    let blinkT = 3, blinkW = 0;
    let visible = true;
    let running = false;

    const LOOPS = new Set(['Idle', 'Thinking']);
    const THINK_AFTER = 14000;   // ms without input before he starts thinking

    // v = take-off speed (units/s); only from the ground so hops don't stack
    const hop = (v) => { if (!reduceMotion && hopY <= 0.001) hopV = Math.max(hopV, v); };

    // ------------------------------------------------------------------ model
    const draco = new DRACOLoader().setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/');
    const loader = new GLTFLoader().setDRACOLoader(draco);
    loader.load('model/kyle_rigged.glb?v=12', (gltf) => {
        const model = gltf.scene;
        model.traverse((o) => {
            if (!o.isMesh) return;
            o.frustumCulled = false;            // skinned bounds don't follow the animation
            const m = o.material;
            if (m && m.map) m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
            if (/Blush/i.test(m?.name || '')) { m.depthWrite = false; }
            if (m && 'sheen' in m) m.sheen = 0;     // sheen reads as a white film on dark cloth here
        });

        // Normalise: feet on y=0, centred on x/z (rest pose).
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());
        model.position.set(-center.x, -box.min.y, -center.z);
        stage.add(model);
        hitBox.setFromCenterAndSize(new THREE.Vector3(0, size.y / 2, 0), size.clone().multiply(new THREE.Vector3(0.75, 1, 1)));

        ['head', 'neck', 'chest'].forEach((n) => {
            const b = model.getObjectByName(n);
            if (b) bones[n] = { o: b, rest: b.quaternion.clone() };
        });
        model.traverse((o) => { if (o.isMesh && o.morphTargetDictionary) faceMeshes.push(o); });
        ['eyeL', 'eyeR'].forEach((n) => {
            const b = model.getObjectByName(n);
            if (b) eyes.push({ o: b, rest: b.position.clone() });
        });

        mixer = new THREE.AnimationMixer(model);
        gltf.animations.forEach((clip) => {
            const a = mixer.clipAction(clip);
            if (LOOPS.has(clip.name)) a.setLoop(THREE.LoopRepeat, Infinity);
            else { a.setLoop(THREE.LoopOnce, 1); a.clampWhenFinished = true; }
            actions[clip.name] = a;
        });
        mixer.addEventListener('finished', (e) => {
            if (actions[current] === e.action) play(restClip(), 0.35);
        });
        play('Idle', 0);
        if (reduceMotion) mixer.timeScale = 0;          // hold a calm idle pose

        // Frame the camera on the model with headroom for hops and waves.
        lookTarget.set(0, size.y * 0.5, 0);
        headAnchor.set(0, size.y * 0.78, 0);    // fixed: never moves with the look itself
        camera.userData.fit = { h: size.y * 1.2, w: size.x * 1.7 };
        resize();

        ready = true;
        canvas.style.opacity = '1';
        stageEl.classList.add('kyle-ready');
        start();
        if (!reduceMotion) setTimeout(() => oneShot('Wave', true), 500);   // hello!
    }, undefined, (err) => {
        console.warn('[kyle3d] model failed to load, showing the portrait.', err);
        showPortrait();
    });

    // ------------------------------------------------------------------ clips
    function restClip() {
        return performance.now() - lastInput > THINK_AFTER ? 'Thinking' : 'Idle';
    }

    function play(name, fade = 0.3) {
        const next = actions[name];
        if (!next) return false;
        const prev = actions[current];
        next.reset().setEffectiveTimeScale(1).setEffectiveWeight(1);
        if (prev && prev !== next) next.crossFadeFrom(prev, fade, false);
        else if (fade) next.fadeIn(fade);
        next.play();
        current = name;
        return true;
    }

    // One-shots (Wave, Happy, Goodbye, Turn) never interrupt each other, except
    // a click (force) which always gets its reaction.
    function oneShot(name, force = false) {
        if (!ready || reduceMotion) return;
        const busy = current && !LOOPS.has(current);
        const now = performance.now();
        if (!force && (busy || now - lastOneShot < 2500)) return;
        lastOneShot = now;
        play(name, 0.25);
    }

    function poke() {               // any input: wake him up from thinking
        lastInput = performance.now();
        if (current === 'Thinking') play('Idle', 0.5);
    }

    // ------------------------------------------------------------------ sizing
    function resize() {
        const r = stageEl.getBoundingClientRect();
        if (!r.width || !r.height) return;
        renderer.setSize(r.width, r.height, false);
        camera.aspect = r.width / r.height;
        const fit = camera.userData.fit || { h: 1.2, w: 0.9 };
        const t = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
        const dist = Math.max(fit.h / 2 / t, fit.w / 2 / (t * camera.aspect));
        camera.position.set(0, lookTarget.y + 0.06, dist);
        camera.lookAt(lookTarget);
        camera.updateProjectionMatrix();
    }
    new ResizeObserver(resize).observe(stageEl);

    // ------------------------------------------------------------------ input
    const raycaster = new THREE.Raycaster();
    const ndc = new THREE.Vector2();
    const worldBox = new THREE.Box3();
    const hitTest = (cx, cy) => {
        const r = canvas.getBoundingClientRect();
        ndc.set(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1);
        raycaster.setFromCamera(ndc, camera);
        stage.updateMatrixWorld();
        worldBox.copy(hitBox).applyMatrix4(stage.matrixWorld);
        return raycaster.ray.intersectsBox(worldBox);
    };

    window.addEventListener('pointermove', (e) => {
        pointer.x = e.clientX; pointer.y = e.clientY; pointer.has = true;
        const now = performance.now();
        const v = Math.hypot(e.clientX - lastPX, e.clientY - lastPY) / Math.max(16, now - lastMoveT) * 1000;
        pointerSpeed = Math.max(pointerSpeed, Math.min(v, 4000));
        lastPX = e.clientX; lastPY = e.clientY; lastMoveT = now;
        poke();
        if (dragging) {
            const dx = e.clientX - lastDragX;
            lastDragX = e.clientX;
            dragMoved = Math.max(dragMoved, Math.abs(e.clientX - dragStartX));
            dragYaw += dx * 0.012;
            return;
        }
        if (e.target === canvas && ready) {
            const h = hitTest(e.clientX, e.clientY);
            if (h && !hovering) { hoverSince = performance.now(); hoverWaved = false; }
            hovering = h;
            canvas.style.cursor = h ? 'grab' : '';
        } else if (hovering) {
            hovering = false;
        }
    }, { passive: true });

    canvas.addEventListener('pointerdown', (e) => {
        if (!ready) return;
        poke();
        dragging = true;
        dragStartX = lastDragX = e.clientX;
        dragMoved = 0;
        canvas.setPointerCapture(e.pointerId);
        canvas.style.cursor = 'grabbing';
    });
    const endDrag = (e) => {
        if (!dragging) return;
        dragging = false;
        dragVel = 0;
        dragYaw = Math.atan2(Math.sin(dragYaw), Math.cos(dragYaw)); // spring back the short way
        canvas.style.cursor = hovering ? 'grab' : '';
        if (dragMoved < 6 && hitTest(e.clientX, e.clientY)) laugh();
    };
    canvas.addEventListener('pointerup', endDrag);
    canvas.addEventListener('pointercancel', () => { dragging = false; });

    // keyboard access: focusable canvas, Enter/Space = laugh
    canvas.tabIndex = 0;
    canvas.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); poke(); laugh(); }
    });

    document.documentElement.addEventListener('mouseleave', () => oneShot('Goodbye'));
    window.addEventListener('keydown', poke, { passive: true });



    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        scrollVel += (y - lastScroll);
        lastScroll = y;
        poke();
    }, { passive: true });

    function laugh() {
        if (!ready) return;
        if (reduceMotion) { spawnHehe(); return; }
        if (current === 'Happy' && actions.Happy.time < 0.6) return;
        oneShot('Happy', true);
        spawnHehe();
    }

    function spawnHehe() {
        [['left', -1], ['right', 1]].forEach(([side], i) => {
            const el = document.createElement('span');
            el.className = `kyle-hehe kyle-hehe--${side}`;
            el.textContent = 'hehe';
            el.style.animationDelay = `${i * 0.18}s`;
            el.setAttribute('aria-hidden', 'true');
            stageEl.appendChild(el);
            el.addEventListener('animationend', () => el.remove());
        });
    }

    // ------------------------------------------------------------------ loop
    new IntersectionObserver(([entry]) => {
        visible = entry.isIntersecting;
        if (visible) start();
    }).observe(stageEl);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) start(); });

    const clock = new THREE.Clock();
    function start() {
        if (running || !ready) return;
        running = true;
        clock.getDelta();
        requestAnimationFrame(tick);
    }

    const tmpV = new THREE.Vector3();
    const tmpV2 = new THREE.Vector3();
    const tmpQ = new THREE.Quaternion();
    const addMorph = (name, v) => {
        if (v <= 0.001) return;
        for (const f of faceMeshes) {
            const i = f.morphTargetDictionary[name];
            if (i !== undefined) f.morphTargetInfluences[i] = Math.min(1, f.morphTargetInfluences[i] + v);
        }
    };
    const offQ = new THREE.Quaternion();
    const offE = new THREE.Euler();
    const damp = (a, b, k, dt) => a + (b - a) * (1 - Math.exp(-k * dt));

    // add a rotation on top of whatever the animation clip set this frame
    function addRot(bone, x, y, z) {
        if (!bone) return;
        offQ.setFromEuler(offE.set(x, y, z));
        bone.o.quaternion.multiply(offQ);
    }

    function tick() {
        if (!visible || document.hidden) { running = false; return; }
        requestAnimationFrame(tick);
        const dt = Math.min(clock.getDelta(), 0.05);
        const m = reduceMotion ? 0 : 1;

        // drift into thinking when left alone
        if (current === 'Idle' && performance.now() - lastInput > THINK_AFTER) play('Thinking', 0.8);

        // Reset the cursor-follow bones first: clips without a head track would otherwise
        // keep last frame's rotation and the added look rotation would pile up (spin).
        bones.neck?.o.quaternion.copy(bones.neck.rest);
        bones.head?.o.quaternion.copy(bones.head.rest);
        for (const f of faceMeshes) f.morphTargetInfluences.fill(0);   // same reason, for the face
        mixer.update(dt);

        // --- where is the pointer relative to his head on screen?
        let ty = 0, tp = 0;
        if (pointer.has && bones.head) {
            // Measure from a fixed anchor, not the live head: the head moving with the look
            // changed the target every frame, which made it shake.
            tmpV.copy(headAnchor).project(camera);
            const r = canvas.getBoundingClientRect();
            const hx = r.left + (tmpV.x * 0.5 + 0.5) * r.width;
            const hy = r.top + (-tmpV.y * 0.5 + 0.5) * r.height;
            const nx = (pointer.x - hx) / (window.innerWidth * 0.5);
            const ny = (pointer.y - hy) / (window.innerHeight * 0.5);
            const ease = (v) => Math.sign(v) * (1 - Math.pow(1 - Math.min(Math.abs(v), 1), 2));
            ty = ease(nx) * 0.45;
            tp = ease(ny) * 0.22;
        }
        // the head is busy during the turn; let the clip drive it
        const follow = current === 'Turn' ? 0 : (current === 'Thinking' ? 0.4 : 1);
        // critically damped spring: smooth start/stop, no overshoot or jitter
        const w = 6;
        look.vy += (w * w * (ty * follow - look.yaw) - 2 * w * look.vy) * dt;
        look.vp += (w * w * (tp * follow - look.pitch) - 2 * w * look.vp) * dt;
        look.yaw += look.vy * dt;
        look.pitch += look.vp * dt;

        // --- timers / springs
        scrollVel = damp(scrollVel, 0, 8, dt);
        if (Math.abs(scrollVel) > 40) hop(Math.min(Math.abs(scrollVel) * 0.003, 0.7));

        // hop spring (y offset), gravity-like pull back to 0
        if (hopY > 0 || hopV > 0) {
            hopV -= 9 * dt;
            hopY += hopV * dt;
            if (hopY <= 0) { hopY = 0; hopV = 0; }
        }

        // drag yaw: free while dragging, springs home after
        if (!dragging) {
            dragVel += (-dragYaw * 30 - dragVel * 8) * dt;
            dragYaw += dragVel * dt;
        }

        // --- stage (whole body)
        stage.position.y = hopY * 0.5 * m;
        stage.rotation.y = dragYaw + look.yaw * 0.2;
        stage.rotation.x = THREE.MathUtils.clamp(scrollVel * 0.001, -0.08, 0.08) * m;

        // --- head / neck follow the cursor, layered on top of the clip
        // (bone axes: Y runs up the neck, X is the nod axis)
        addRot(bones.neck, look.pitch * 0.35, look.yaw * 0.3, 0);
        addRot(bones.head, look.pitch * 0.65, look.yaw * 0.6, 0);

        expressions(dt);
        renderer.render(scene, camera);
    }

    // Curious face, layered on Idle only (the other clips own the face).
    function expressions(dt) {
        pointerSpeed = damp(pointerSpeed, 0, 6, dt);
        const idle = current === 'Idle';
        const near = hovering || dragging;
        const moving = performance.now() - lastMoveT < 1500;
        // wave only when the cursor actually rests on him, not when it sweeps across
        if (hovering && !hoverWaved && performance.now() - hoverSince > 450) { hoverWaved = true; oneShot('Wave'); }
        // slow, soft blends so the face never snaps between expressions
        mood.curious = damp(mood.curious, idle && moving && !near ? 1 : 0, 2.2, dt);
        mood.happy = damp(mood.happy, idle && near ? 1 : 0, 2.5, dt);
        const fast = pointerSpeed > 2600 ? 1 : 0;          // only a really quick flick says "oh"
        mood.oh = damp(mood.oh, fast, mood.oh < fast ? 3 : 1.5, dt);

        // quick blinks while the eyes are open (open -> ^ -> open)
        blinkT -= dt;
        if (blinkT <= 0) { blinkW = 1; blinkT = 2.5 + Math.random() * 3.5; }
        blinkW = Math.max(0, blinkW - dt * 7);
        const blink = Math.sin(blinkW * Math.PI);

        const c = mood.curious;
        const side = THREE.MathUtils.clamp(look.yaw / 0.55, -1, 1);    // + = cursor on his left (screen right)
        const up = THREE.MathUtils.clamp(-look.pitch / 0.3, -1, 1);    // + = cursor above his head
        addMorph('EyeOpen_L', c * (1 - blink));
        addMorph('EyeOpen_R', c * (1 - blink));
        addMorph('BrowRaise_L', c * (Math.max(side, 0) * 0.9 + Math.max(up, 0) * 0.5));
        addMorph('BrowRaise_R', c * (Math.max(-side, 0) * 0.9 + Math.max(up, 0) * 0.5));
        addMorph('MouthOh', c * mood.oh);
        addMorph('MouthSmile', c * (1 - mood.oh));
        addMorph('EyeSquint', mood.happy * 0.7);
        addMorph('BlushHot', mood.happy * 0.6);

        // pupils drift toward the cursor (world offset -> head space)
        if (bones.head && eyes.length) {
            bones.head.o.getWorldQuaternion(tmpQ).invert();
            tmpV2.set(side * 0.006 * c, up * 0.005 * c, 0).applyQuaternion(tmpQ);
            for (const e of eyes) e.o.position.copy(e.rest).add(tmpV2);
        }
    }
}
