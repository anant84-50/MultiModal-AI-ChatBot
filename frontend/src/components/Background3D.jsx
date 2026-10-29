import React, { useEffect, useRef } from 'react';

/**
 * Interactive 3D Golden Mesh & Constellation Background
 * Uses pure HTML5 Canvas with 3D perspective projection (X, Y, Z coordinates),
 * subtle particle physics, mouse-responsive rotation, and golden filament connections.
 */
export default function Background3D() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Mouse coordinates for gentle 3D parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetRotX = 0;
    let targetRotY = 0;
    let rotX = 0;
    let rotY = 0;

    const handleMouseMove = (e) => {
      mouseX = (e.clientX - width / 2) / (width / 2);
      mouseY = (e.clientY - height / 2) / (height / 2);
      targetRotY = mouseX * 0.3;
      targetRotX = -mouseY * 0.3;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // 3D Particles
    const PARTICLE_COUNT = 55;
    const particles = [];
    const focalLength = 400;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: (Math.random() - 0.5) * 1200,
        y: (Math.random() - 0.5) * 800,
        z: (Math.random() - 0.5) * 600,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        vz: (Math.random() - 0.5) * 0.35,
        radius: Math.random() * 2.2 + 1.2,
        baseAlpha: Math.random() * 0.6 + 0.25,
      });
    }

    const render = () => {
      // Smooth interpolation for 3D rotation
      rotX += (targetRotX - rotX) * 0.05;
      rotY += (targetRotY - rotY) * 0.05;

      ctx.clearRect(0, 0, width, 0, height);

      // Deep luxurious background gradient with golden ambient glow
      const bgGrad = ctx.createRadialGradient(
        width / 2 + mouseX * 80,
        height / 2 + mouseY * 80,
        50,
        width / 2,
        height / 2,
        Math.max(width, height) * 0.8
      );
      bgGrad.addColorStop(0, '#131109');
      bgGrad.addColorStop(0.5, '#0a0907');
      bgGrad.addColorStop(1, '#050505');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      const cosY = Math.cos(rotY);
      const sinY = Math.sin(rotY);
      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);

      const projected = [];

      // Update and project 3D points
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Move particle
        p.x += p.vx;
        p.y += p.vy;
        p.z += p.vz;

        // Wrap boundaries in 3D box
        if (p.x < -600) p.x = 600;
        if (p.x > 600) p.x = -600;
        if (p.y < -400) p.y = 400;
        if (p.y > 400) p.y = -400;
        if (p.z < -300) p.z = 300;
        if (p.z > 300) p.z = -300;

        // 3D rotation around Y and X axis
        // Rotate around Y
        const x1 = p.x * cosY - p.z * sinY;
        const z1 = p.z * cosY + p.x * sinY;

        // Rotate around X
        const y2 = p.y * cosX - z1 * sinX;
        const z2 = z1 * cosX + p.y * sinX + 500; // shift forward so z > 0

        if (z2 > 10) {
          const scale = focalLength / z2;
          const projX = width / 2 + x1 * scale;
          const projY = height / 2 + y2 * scale;
          projected.push({
            x: projX,
            y: projY,
            scale,
            radius: p.radius * scale,
            alpha: Math.min(1, Math.max(0.1, (scale * 0.8) * p.baseAlpha)),
          });
        } else {
          projected.push(null);
        }
      }

      // Draw connecting filaments in 3D golden hue
      ctx.lineWidth = 0.8;
      for (let i = 0; i < projected.length; i++) {
        const p1 = projected[i];
        if (!p1) continue;

        for (let j = i + 1; j < projected.length; j++) {
          const p2 = projected[j];
          if (!p2) continue;

          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 130) {
            const filamentAlpha = (1 - dist / 130) * 0.22 * Math.min(p1.alpha, p2.alpha);
            ctx.strokeStyle = `rgba(212, 175, 55, ${filamentAlpha})`;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      // Draw glowing golden 3D orbs
      for (let i = 0; i < projected.length; i++) {
        const pt = projected[i];
        if (!pt) continue;

        // Core gold point
        ctx.fillStyle = `rgba(245, 197, 66, ${pt.alpha})`;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, Math.max(1, pt.radius), 0, Math.PI * 2);
        ctx.fill();

        // Subtle specular halo around larger particles
        if (pt.radius > 2) {
          ctx.fillStyle = `rgba(212, 175, 55, ${pt.alpha * 0.35})`;
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, pt.radius * 2.5, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="canvas-3d-background"
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  );
}
