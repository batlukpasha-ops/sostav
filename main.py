from typing import List

import psycopg
from fastapi import FastAPI, HTTPException, status

from database import get_connection
from models import Like, LikeCreate, Match, Profile, ProfileCreate, User, UserCreate


app = FastAPI(title="Dating Service MVP")


def get_user_or_404(user_id: int) -> dict:
    """Ищем пользователя. Если его нет, сразу возвращаем ошибку 404."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, age FROM users WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (name, email, age)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, email, age
                    """,
                    (user.name, user.email, user.age),
                )
                created_user = cur.fetchone()
                conn.commit()
                return created_user
    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )


@app.get("/users", response_model=List[User])
def get_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, age FROM users ORDER BY id")
            return cur.fetchall()


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    return get_user_or_404(user_id)


@app.post("/profiles", response_model=Profile, status_code=status.HTTP_201_CREATED)
def create_profile(profile: ProfileCreate):
    get_user_or_404(profile.user_id)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO profiles (user_id, city, bio)
                    VALUES (%s, %s, %s)
                    RETURNING id, user_id, city, bio
                    """,
                    (profile.user_id, profile.city, profile.bio),
                )
                created_profile = cur.fetchone()
                conn.commit()
                return created_profile
    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль для этого пользователя уже существует",
        )


@app.get("/profiles/{user_id}", response_model=Profile)
def get_profile(user_id: int):
    get_user_or_404(user_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, user_id, city, bio FROM profiles WHERE user_id = %s",
                (user_id,),
            )
            profile = cur.fetchone()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден",
        )

    return profile


@app.post("/likes", response_model=Like, status_code=status.HTTP_201_CREATED)
def create_like(like: LikeCreate):
    if like.from_user_id == like.to_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя лайкнуть самого себя",
        )

    get_user_or_404(like.from_user_id)
    get_user_or_404(like.to_user_id)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id FROM likes
                    WHERE from_user_id = %s AND to_user_id = %s
                    """,
                    (like.from_user_id, like.to_user_id),
                )
                existing_like = cur.fetchone()

                if existing_like is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Такой лайк уже существует",
                    )

                cur.execute(
                    """
                    INSERT INTO likes (from_user_id, to_user_id)
                    VALUES (%s, %s)
                    RETURNING id, from_user_id, to_user_id
                    """,
                    (like.from_user_id, like.to_user_id),
                )
                created_like = cur.fetchone()

                # Если второй пользователь уже лайкнул первого, создаем match.
                cur.execute(
                    """
                    SELECT id FROM likes
                    WHERE from_user_id = %s AND to_user_id = %s
                    """,
                    (like.to_user_id, like.from_user_id),
                )
                reverse_like = cur.fetchone()

                if reverse_like is not None:
                    user1_id = min(like.from_user_id, like.to_user_id)
                    user2_id = max(like.from_user_id, like.to_user_id)
                    cur.execute(
                        """
                        INSERT INTO matches (user1_id, user2_id)
                        VALUES (%s, %s)
                        ON CONFLICT (user1_id, user2_id) DO NOTHING
                        """,
                        (user1_id, user2_id),
                    )

                conn.commit()
                return created_like
    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой лайк уже существует",
        )


@app.get("/matches/{user_id}", response_model=List[Match])
def get_matches(user_id: int):
    get_user_or_404(user_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user1_id, user2_id
                FROM matches
                WHERE user1_id = %s OR user2_id = %s
                ORDER BY id
                """,
                (user_id, user_id),
            )
            return cur.fetchall()
