def error():
    raise RuntimeError('error')

if __name__ == '__main__':
    try:
        error()
    except RuntimeError as re:
        raise re
    finally:
        print "can't do it."
