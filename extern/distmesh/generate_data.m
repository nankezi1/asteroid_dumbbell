% generate sphere and ellipsoid meshes

a = 1;
b = 2;
c = 3;

fd_sphere=@(p) dsphere(p,0,0,0,0.5);
fd_ellipsoid=@(p) p(:,1).^2/a^2+p(:,2).^2/b^2+p(:,3).^2/c^2-1;


[v,f]=distmeshsurface(fd_sphere,@huniform,0.01,1.1*[-1,-1,-1;1,1,1]);
save('sphere_distmesh.mat', 'v', 'f');

[v,f]=distmeshsurface(fd_ellipsoid,@huniform,0.1,1.1 * [-a, -b, -c; a, b, c]);
