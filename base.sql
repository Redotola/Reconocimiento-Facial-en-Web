-- SQLBook: Code

/*Tabka de tipo de usuarios*/
CREATE TABLE IF NOT EXISTS tip_usu (
  id_tip_usu int(11) NOT NULL,
  nom_tip_usu varchar(20) NOT NULL,
  PRIMARY KEY (id_tip_usu)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Tabla de los tipos de usuarios
Necesario para determinar y manejar sesiones, es de crucial importancia que no se cambien los datos dentro de esta
insercion ya que con esto validara la entrada al sistema o diversas funciones!
*/
INSERT INTO tip_usu (id_tip_usu, nom_tip_usu) VALUES
(1, 'Administrador'),
(2, 'Empleado'),
(3, 'Recursos humanos');

/*Tipo de horarios del empleado en el sistema*/
create table horario(
  id_hora int AUTO_INCREMENT,
  nombre varchar (15),
  PRIMARY KEY(id_hora)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Inserciones importantes para el tipo de horario que usara el usuario*/
insert into horario (id_hora,nombre) values (1,'Nocturno'), (2,'Matutino'), (3,'Vespertino');

/*Tabla de usuarios para registro y acceso al sistema*/
CREATE TABLE IF NOT EXISTS users (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(20) NOT NULL,
  email varchar(100) NOT NULL,
  password varchar(100) NOT NULL,
  id_tip_usu int(11) NOT NULL,
  id_hora int not null,
  PRIMARY KEY (id),
  KEY id_tip_usu (id_tip_usu),
  Foreign Key (id_hora) REFERENCES horario(id_hora)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
COMMIT;

/*Inserciones necesarias para prueba de usuarios en el sistema 
Importante insertar usuario de tipo administrador id_tip_usu=1! 
Ya que sin el usuario aadministrador no se puede acceder al sistema sin usuarios*/

insert into users (name,email,password,id_tip_usu,id_hora) VALUES ('Axl','axl@gmail.com','lol',1,1);
insert into users (name,email,password,id_tip_usu,id_hora) VALUES ('Lalo','lalo@gmail.com','lol',3,3);
insert into users (name,email,password,id_tip_usu,id_hora) VALUES ('Antunez','antunez@gmail.com','lol',2,2);

/*Creacion de tabla asistencia*/
create table asistencia(

  id int PRIMARY KEY AUTO_INCREMENT,
  hora TIME not null,
  fecha date not null,
  email_emp varchar(30) not null,
  estado varchar (20) not null

)ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

/*Creacion de tabla justificantes*/
CREATE TABLE justificantes(
id int PRIMARY KEY not null AUTO_INCREMENT,
empcorreo varchar(100),
fecha date not null,
motivo varchar(200) not null,
estado VARCHAR (15) not null,
id_emp int not null,
Foreign Key (empcorreo) REFERENCES users(email),
Foreign Key (id_emp) REFERENCES users(id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Trigger de estado del justificante*/
create trigger estadojustificante before insert on justificantes
for each row
	begin
	set  new.estado = "En espera";
end;

/*Tabla de hora inicial*/

drop table horainicial;
create table horainicial(
  idinicial int AUTO_INCREMENT,
  hora_inicial time NOT NULL,
  PRIMARY KEY(idinicial)
)ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Inserciones para mostrar datos de tipo time en tabla hora inicial*/
insert into horainicial (hora_inicial) values ('00:00:00'),('01:00:00'),('2:00:00'),('3:00:00'),
('4:00:00'),('5:00:00'),('6:00:00'),('7:00:00'),('8:00:00'),('9:00:00'),('10:00:00'),('11:00:00'),
('12:00:00'),('13:00:00'),('14:00:00'),('15:00:00'),('16:00:00'),('17:00:00'),('18:00:00'),
('19:00:00'),('20:00:00'),('21:00:00'),('22:00:00'),('23:00:00');


/*Trigger para estado de asistencia*/
create trigger asistencia before insert on asistencia
for each row
    BEGIN
    set new.hora=TIME(NOW());
    set new.fecha=DATE(NOW());
    set new.estado="Asistencia";
end;

/*Creacion de table hora final de jornada*/
create table horafinal(
  idfinal int NOT NULL AUTO_INCREMENT,
  hora_final time NOT NULL,
  PRIMARY KEY(idfinal)
)ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Inserciones obligatorias para mostrar opciones de tipo time en tabla hora final*/
insert into horafinal (hora_final) values ('00:00:00'),('01:00:00'),('2:00:00'),('3:00:00'),
('4:00:00'),('5:00:00'),('6:00:00'),('7:00:00'),('8:00:00'),('9:00:00'),('10:00:00'),('11:00:00'),
('12:00:00'),('13:00:00'),('14:00:00'),('15:00:00'),('16:00:00'),('17:00:00'),('18:00:00'),
('19:00:00'),('20:00:00'),('21:00:00'),('22:00:00'),('23:00:00');
select * from horafinal;

/*Tabla horas que define el horario del usuario*/
create table horas(
  idhoras int AUTO_INCREMENT,
  email varchar(100) NOT NULL,
  ini time not null,
  fin time not null,
  PRIMARY KEY (idhoras),
  Foreign Key (ini) REFERENCES horainicial(hora_inicial),
  Foreign Key (fin) REFERENCES horafinal(hora_final)
)ENGINE=MyISAM DEFAULT CHARSET=latin1;

SELECT* from horas;
/*tabla de vacaciones*/
create table vacaciones(
empcor varchar(100),
fecha date not null,
moti varchar(200) not null,
estado varchar(15) not null,
id_emplea int not null,
Foreign Key (empcor) REFERENCES users(email),
Foreign Key (id_emplea) REFERENCES users(id)
)ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Trigger de estado de vacaciones*/
create trigger estadovacaciones before insert on vacaciones
for each row
	begin
	set  new.estado = "En espera";
end;

/*tabla de permisos*/
create table permisos(
correo varchar(100),
fecha date not null,
motivo varchar(200) not null,
estado varchar (15) not null,
id_empleado int not null,
Foreign Key (correo) REFERENCES users(email),
Foreign Key (id_empleado) REFERENCES users(id)
)ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Trigger para el estado de permisos*/
create trigger estadopermisos before insert on permisos
for each row
	begin
	set  new.estado = "En espera";
end;


/*Trigger para el estado de asistencia*/
create trigger estadoasistencia before insert on asistencia
for each row
  BEGIN
  set new.estado = "Asistencia";
end;

