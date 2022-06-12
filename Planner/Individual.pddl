(define (problem Individual)
	(:domain World)
	(:objects
		bob
		maggie
		anne
		islandeast
		store
		mountaineast
		neighborhouse
		food5
		antidote2
		food1
		food2
		toolkit2
		wood1
		wood3
		zombie
		bigzombie
	)
	(:init
		(istool toolkit2)
		(iswood wood1)
		(alive anne)
		(healthy anne)
		(iswood wood3)
	)
	(:goal
		(and
			(at bob store)
			(has anne wood3)
		)
	)
)