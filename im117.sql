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

create table mantenimiento(
     id int auto_increment primary key,
     nombreA varchar(20) not null,
     tipoServicio enum('Mantenimiento', 'Reparación') not null,
     descripcionFalla text not null,
	 fecha date not null
);

drop table mantenimiento;

insert into mantenimiento(nombreA, tipoServicio, descripcionFalla, fecha) values
     ('AK-47', 'Mantenimiento', 'Revisión general del sistema de disparo', '2024-11-22'),
     ('M16', 'Reparación', 'Cambio de resorte en el mecanismo de disparo', '2024-11-20'),
     ('Glock 19', 'Mantenimiento', 'Limpieza y engrase completo', '2024-11-18');

select * from mantenimiento;

create table pedidos(
     id int auto_increment primary key,
     equipo varchar(50) not null,
     cantidad int not null,
     proveedor varchar(30) not null,
	 fecha date not null,
     comentarios text
);

insert into pedidos(equipo, cantidad, proveedor, fecha, comentarios) values
     ('Pistola Glock 17', 10, 'Proveedor A', '2024-11-01', 'Se requiere entrega antes del 15 de noviembre'),
     ('Rifle AR-15', 5, 'Proveedor B', '2024-11-02', 'Pedido urgente'),
     ('Municiones 9mm', 500, 'Proveedor D', '2024-11-05', 'Incluye embalaje adicional');
     
select * from pedidos;
drop table pedidos;