s3-saver
========

Utility class in Python for finding, saving, and deleting files that are either on Amazon S3, or on the local filesystem.

The idea behind this, is that you can pass exactly the same data (in particular, the same file path) irrespective of whether you're working with a local or S3-based file. All you have to do, on each call, is to specify 's3' for S3, or None for local.

This is great for apps where all files are stored on the local filesystem in one environment (e.g. development), and on S3 in another environment (e.g. production). The only thing you have to work out at run-time, is whether to specify 's3' or None - the rest of your file-handling code stays the same.


Example
-------

For a complete, working Flask app that demonstrates s3-saver in action, have a look at `flask-s3-save-example <https://github.com/Jaza/flask-s3-save-example>`_.


Usage
-----

.. code:: python

    from io import BytesIO
    import os
    from s3_saver import S3Saver

    bucket_name = 's3-test-foobar-whizbang'

    # Absolute path to your project's root
    static_root_parent = '/home/mrfoo/pyprojectfoo'

    # Absolute path to dir where file gets saved
    base_path = os.path.join(static_root_parent, 'static/uploads')

    # For a dummy object that attributes can get saved to.
    # In most real-life cases, this would be an ORM model
    # (e.g. inherited from django.db.models.Model for Django, or
    # sqlalchemy.ext.declarative.declarative_base() for SQLAlchemy).
    class Thingy(object):
        pass

    # Load a sample file into a temp object
    filename = 'whizbang.jpg'
    filepath = os.path.join(base_path, filename)
    thingy = Thingy()
    temp_file = BytesIO()

    # Read a local file into a BytesIO object.
    # For most real-life cases, you'd instead load a file uploaded
    # in a HTTP POST request into a BytesIO. E.g. in a Flask route:
    # from flask import request
    # request.files['thingy_image'].save(temp_file)
    f = open('/home/mrfoo/photos/hobbies/whizbang.jpg', 'rb')
    f.seek(0)
    one_mb = 1024*1024

    t = f.read(one_mb)
    while t:
        temp_file.write(t)
        t = f.read(one_mb)

    f.close()

    # Initialize the saver
    image_saver = S3Saver(
        storage_type='s3',
        bucket_name=bucket_name,
        access_key_id='XXXXX',
        access_key_secret='YYYYY',
        field_name='image',
        storage_type_field='image_storage_type',
        bucket_name_field='image_storage_bucket_name',
        filesize_field='image_filesize',
        base_path=base_path,
        static_root_parent=static_root_parent)

    # Save the file to S3, in the specified bucket,
    # at 'static/uploads/whizbang.jpg'
    image_saver.save(temp_file, filename, thingy)

    print(thingy.image) # 'whizbang.jpg'
    print(thingy.image_storage_type) # 's3'
    print(thingy.image_storage_bucket_name) # 's3-test-foobar-whizbang'

    # In most real-life cases, you'd persist the 'thingy' object
    # at this point. E.g. in SQLAlchemy:
    # db.session.add(thingy)
    # db.session.commit()

    # Now save the file locally,
    # at '/home/mrfoo/pyprojectfoo/static/uploads/whizbang.jpg'
    image_saver.storage_type = None
    image_saver.save(temp_file, filename, thingy)

    print(thingy.image) # 'whizbang.jpg'
    print(thingy.image_storage_type) # ''
    print(thingy.image_storage_bucket_name) # ''

    # Find files on S3, searching by key prefix.
    # Prints:
    # [u'static/uploads/whizbang.jpg']
    print([k.name for k in image_saver.find_by_path(
        '/home/mrfoo/pyprojectfoo/static/uploads/whizb',
        storage_type='s3',
        bucket_name=bucket_name)])

    # Find files locally, searching by glob.
    # Prints:
    # ['/home/mrfoo/pyprojectfoo/static/uploads/whizbang.jpg']
    print([k for k in image_saver.find_by_path(
        '/home/mrfoo/pyprojectfoo/static/uploads/whizb',
        storage_type=None,
        bucket_name=bucket_name)])

    # Delete the file on S3.
    image_saver.delete(
        '/home/mrfoo/pyprojectfoo/static/uploads/whizbang.jpg',
        storage_type='s3',
        bucket_name=bucket_name)

    # Delete the file locally.
    image_saver.delete(
        '/home/mrfoo/pyprojectfoo/static/uploads/whizbang.jpg',
        storage_type=None,
        bucket_name=bucket_name)
