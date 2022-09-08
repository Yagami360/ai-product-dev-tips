package main

type UserEntity struct {
	id   int64
	name string
}

type User interface {
	Update(userEntity *UserEntity) error
}
