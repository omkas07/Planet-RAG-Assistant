import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "space_db"

PLANETS = [
    # name, type, diameter_km, mass_earths, distance_au, orbital_period_days, mean_temp_c, has_rings
    ("Mercury", "terrestrial",   4879,   0.055,  0.39,    88.0,  167, False),
    ("Venus",   "terrestrial",  12104,   0.815,  0.72,   224.7,  464, False),
    ("Earth",   "terrestrial",  12756,   1.000,  1.00,   365.2,   15, False),
    ("Mars",    "terrestrial",   6792,   0.107,  1.52,   687.0,  -65, False),
    ("Jupiter", "gas giant",   142984, 317.800,  5.20,  4331.0, -110, True),
    ("Saturn",  "gas giant",   120536,  95.200,  9.54, 10747.0, -140, True),
    ("Uranus",  "ice giant",    51118,  14.500, 19.19, 30589.0, -195, True),
    ("Neptune", "ice giant",    49528,  17.100, 30.07, 59800.0, -200, True),
]


def main():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        charset="utf8mb4",
    )

    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
            cur.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute(f"USE {DB_NAME}")

            cur.execute("""
                CREATE TABLE planets (
                    id                  INT PRIMARY KEY AUTO_INCREMENT,
                    name                VARCHAR(50)  NOT NULL UNIQUE,
                    type                VARCHAR(30)  NOT NULL,
                    diameter_km         INT          NOT NULL,
                    mass_earths         DECIMAL(8,3) NOT NULL,
                    distance_au         DECIMAL(5,2) NOT NULL,
                    orbital_period_days DECIMAL(8,1) NOT NULL,
                    mean_temp_c         INT          NOT NULL,
                    has_rings           BOOLEAN      NOT NULL
                )
            """)

            cur.executemany("""
                INSERT INTO planets
                    (name, type, diameter_km, mass_earths, distance_au,
                     orbital_period_days, mean_temp_c, has_rings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, PLANETS)

        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT name, diameter_km, mean_temp_c FROM planets ORDER BY id")
            for row in cur.fetchall():
                print(row)
        print(f"\n✓ {DB_NAME}.planets ready, {len(PLANETS)} rows")

    except Exception as e:
        conn.rollback()
        print("✗ error:", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()