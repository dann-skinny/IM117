create database im117;
use im117;

create table usuarios (
	id int auto_increment primary key,
    usuario varchar(50) not null,
    rol varchar(40) not null,
    password varchar(10) not null
);

drop table usuarios;

insert into usuarios(usuario, rol, password) values
	('Elmer Homero', 'almacen', '12345'),
    ('Esteban Quito', 'mantenimiento', '12345'),
    ('Elsa Pato', 'ventas', '12345'),
    ('Lola Mento', 'proveedores', '12345'),
    ('Zoyla Vaca', 'envios', '12345');
    
select * from usuarios;