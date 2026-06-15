CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE genres (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	CONSTRAINT pk_genres PRIMARY KEY (id), 
	CONSTRAINT uq_genres_name UNIQUE (name)
);
CREATE TABLE images (
	id VARCHAR(100) NOT NULL, 
	file_name VARCHAR(100) NOT NULL, 
	mime_type VARCHAR(100) NOT NULL, 
	md5_hash VARCHAR(100) NOT NULL, 
	object_id INTEGER, 
	object_type VARCHAR(100), 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_images PRIMARY KEY (id), 
	CONSTRAINT uq_images_md5_hash UNIQUE (md5_hash)
);
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	description TEXT NOT NULL, 
	CONSTRAINT pk_roles PRIMARY KEY (id), 
	CONSTRAINT uq_roles_name UNIQUE (name)
);
CREATE TABLE books (
	id INTEGER NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	short_desc TEXT NOT NULL, 
	full_desc TEXT NOT NULL, 
	year INTEGER, 
	publisher VARCHAR(200), 
	pages INTEGER, 
	author_name VARCHAR(200) NOT NULL, 
	rating_sum INTEGER NOT NULL, 
	rating_num INTEGER NOT NULL, 
	cover_image_id VARCHAR(100), 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_books PRIMARY KEY (id), 
	CONSTRAINT fk_books_cover_image_id_images FOREIGN KEY(cover_image_id) REFERENCES images (id)
);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	first_name VARCHAR(100) NOT NULL, 
	last_name VARCHAR(100) NOT NULL, 
	middle_name VARCHAR(100), 
	login VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(200) NOT NULL, 
	role_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_users PRIMARY KEY (id), 
	CONSTRAINT fk_users_role_id_roles FOREIGN KEY(role_id) REFERENCES roles (id), 
	CONSTRAINT uq_users_login UNIQUE (login)
);
CREATE TABLE book_genre (
	book_id INTEGER NOT NULL, 
	genre_id INTEGER NOT NULL, 
	CONSTRAINT pk_book_genre PRIMARY KEY (book_id, genre_id), 
	CONSTRAINT fk_book_genre_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_book_genre_genre_id_genres FOREIGN KEY(genre_id) REFERENCES genres (id)
);
CREATE TABLE page_views (
	id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	user_id INTEGER, 
	session_id VARCHAR(100), 
	viewed_at DATETIME NOT NULL, 
	CONSTRAINT pk_page_views PRIMARY KEY (id), 
	CONSTRAINT fk_page_views_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_page_views_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE reviews (
	id INTEGER NOT NULL, 
	rating INTEGER NOT NULL, 
	text TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	book_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	CONSTRAINT pk_reviews PRIMARY KEY (id), 
	CONSTRAINT fk_reviews_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_reviews_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
