import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )


def worker_with(lock, message):
    with lock:
        n = 0
        while n < 10:
            logging.debug(f"Contamos {n}:{message}")
            n += 1


if __name__ == '__main__':
    lock = threading.Lock()
    w = threading.Thread(target=worker_with, args=(lock, "tarea1"))
    nw = threading.Thread(target=worker_with, args=(lock, "tarea2"))

    w.start()
    nw.start()