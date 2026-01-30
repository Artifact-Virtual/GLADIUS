import React, { useEffect, useRef } from 'react';

export const CosmicBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    class Star {
      x: number;
      y: number;
      z: number;
      size: number;
      
      constructor() {
        this.x = Math.random() * canvas!.width - canvas!.width / 2;
        this.y = Math.random() * canvas!.height - canvas!.height / 2;
        this.z = Math.random() * 1000;
        this.size = Math.random() * 2;
      }

      update() {
        this.z -= 2;
        if (this.z <= 0) {
          this.z = 1000;
          this.x = Math.random() * canvas!.width - canvas!.width / 2;
          this.y = Math.random() * canvas!.height - canvas!.height / 2;
        }
      }

      draw(ctx: CanvasRenderingContext2D) {
        const x = (this.x / this.z) * 300 + canvas!.width / 2;
        const y = (this.y / this.z) * 300 + canvas!.height / 2;
        const size = (1 - this.z / 1000) * this.size;

        ctx.fillStyle = `rgba(59, 130, 246, ${1 - this.z / 1000})`;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const stars: Star[] = Array.from({ length: 200 }, () => new Star());

    let animationId: number;
    const animate = () => {
      ctx.fillStyle = 'rgba(10, 14, 39, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      stars.forEach(star => {
        star.update();
        star.draw(ctx);
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0 opacity-30"
    />
  );
};
