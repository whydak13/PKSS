init;
Fcobmax=40;
init;
Yb=0;
Yk=0;
K=5; % Regulator gain
Ki=0.01;
t=0;
t0=0;
Tzco=70;
sum=0;
set_point1=20;
K=1; % Regulator gain
t=0;
t0=0;
time=0;
delT=1;
Tzco=60;
Fcob=K*(set_point1-Tr);
Fcob=min(Fcob,  Fcobmax);
Fcob=max(Fcob,0);
t = tcpip('192.168.1.101',1234, 'NetworkRole', 'client');
set(t,'InputBufferSize', 5000)
set(t,'Timeout',20000)
fopen(t)
init_json=struct('type','init','src','budynek1');
init_frame=savejson('',init_json);
fwrite(t,init_frame);
rec_len=t.BytesAvailable
while(t.BytesAvailable==0)
end

data = fread(t, t.BytesAvailable)
json_rec=JSON.parse(data')


json_data_send=struct('type','data','src','budynek1','T_pcob1',Tpco,'F_cob1',Fcob,'T_r1',Tr, 'U_b1',Fcob/Fcobmax) 
data_send_frame=savejson('',json_data_send)
fwrite(t, data_send_frame)

while(t.BytesAvailable==0)
end
    % inputs %%%%
 frame_rec = fread(t, t.BytesAvailable,'char');
 json_rec=JSON.parse(char(frame_rec'));

while(1)
    
global Fcob
sum=sum+(set_point1-Tr);
Fcob=K*(set_point1-Tr)+Ki*sum;
Fcob=min(Fcob,  Fcobmax);
 global Tpco
 global Tr
 
[Tk,Yk] = ode45(@kal,[time time+delT],Tpco );
Tpco=max(Yk);
[Tb,Yb] =ode45(@bud,[time time+delT],Tr ); %Yb(length(Yb)) [Tb,Yb] =
time=time+delT;
Tr=Yb(length(Yb),1);
Tpco
Tr
figure(1)
hold on
subplot(2,1,1)
plot(Tb,Yb(:,1))
subplot(2,1,2)
plot(Tk,Yk(:,1)) 

json_data_send=struct('type','data','src','budynek1','T_pcob1',Tpco,'F_cob1',Fcob,'T_r1',Tr,'U_b1',Fcob/Fcobmax) 
data_send_frame=savejson('',json_data_send)

fwrite(t, data_send_frame)

while(t.BytesAvailable==0)
end
    % inputs %%%%
 frame_rec = fread(t, t.BytesAvailable,'char');
 json_rec=JSON.parse(char(frame_rec'));
if(isfield(json_rec,'kp_b1'))
        K=json_rec.kp_b1;
    end
        if(isfield(json_rec,'ki_b1'))
        Ki=json_rec.T_zco;
        end
        if(isfield(json_rec,'T_b1'))
        set_point1=json_rec.T_b1;
        end
global Tzco
global To
while(flag==0)
  frame_rec = fread(t, t.BytesAvailable,'char');
 json_rec=JSON.parse(char(frame_rec'));
    flag=1;
    
    if(isfield(json_rec,'T_zco'))
        Tzco=json_rec.T_zco;
    else
        flag=0;
    end
    if(isfield(json_rec,'T_o'))
        To=json_rec.T_o;

    else
        flag=0;
    end
     if(isfield(json_rec,'trzy_miliony'))
        delT=json_rec.trzy_miliony*60;

    else
        flag=0;
     end
   

    

end




end
