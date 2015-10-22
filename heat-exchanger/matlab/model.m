% parametry
% M_M = sym('M_M');
% c_wym = sym('c_wym');
% F_ZM = sym('F_ZM');
% g_w = sym('g_w');
% c_w = sym('c_w');
% k_w = sym('k_w');
% M_CO = sym('M_CO');
% F_ZCO = sym('F_ZCO');
% syms M_M, c_wym, F_ZM, g_w, c_w, k_w, M_CO, F_ZCO
% probkowanie
syms h
syms t

% model ciągły
% x1 - T_PM
% x2 - T_ZCO
% u1 - T_ZM
% u2 - T_PCO
% x' = Ax + Bu
% y = x
syms a11 a12 a21 a22 b11 b22
% A = [ -(F_ZM * g_w * c_w + k_w) / (M_M * c_wym), k_w / (M_M * c_wym);
%     k_w / (M_CO * c_wym), -(F_ZCO * g_w * c_w + k_w) / (M_CO * c_wym)];
% B = [ (F_ZM * g_w * c_w) / (M_M * c_wym), 0;
%     0, (F_ZCO * g_w * c_w) / (M_CO * c_wym)];
A = [a11, a12; a21, a22];
B = [b11, 0; 0, b22];
C = [1, 0;
    0, 1];
D = [0; 0];

Ah = expm(A * h);
Bh = int(expm(A * t) * B, t, 0, h)
Ch = C;
Dh = [0; 0];


