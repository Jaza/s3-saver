__version__ = '0.1.2'

from glob import glob
import os
import re

from boto.s3.connection import S3Connection
from boto.exception import S3ResponseError
from boto.s3.key import Key


class S3Saver(object):
    """
    Saves files to Amazon S3 (or default local storage).
    """

    def __init__(self, storage_type=None, bucket_name=None,
                 access_key_id=None, access_key_secret=None,
                 acl='public-read', field_name=None,
                 storage_type_field=None, bucket_name_field=None,
                 filesize_field=None, base_path=None,
                 permission=0o666, static_root_parent=None):
        if storage_type and (storage_type != 's3'):
            raise ValueError('Storage type "%s" is invalid, the only supported storage type (apart from default local storage) is s3.' % storage_type)

        self.storage_type = storage_type
        self.bucket_name = bucket_name
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.acl = acl
        self.field_name = field_name
        self.storage_type_field = storage_type_field
        self.bucket_name_field = bucket_name_field
        self.filesize_field = filesize_field
        self.base_path = base_path
        self.permission = permission
        self.static_root_parent = static_root_parent

    def _get_path(self, filename):
        if not self.base_path:
            raise ValueError('S3Saver requires base_path to be set.')

        if callable(self.base_path):
            return os.path.join(self.base_path(), filename)
        return os.path.join(self.base_path, filename)

    def _get_s3_path(self, filename):
        if not self.static_root_parent:
            raise ValueError('S3Saver requires static_root_parent to be set.')

        return re.sub('^\/', '', self._get_path(filename).replace(self.static_root_parent, ''))

    def _delete_local(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def _delete_s3(self, filename, bucket_name):
        conn = S3Connection(self.access_key_id, self.access_key_secret)
        bucket = conn.get_bucket(bucket_name)

        if type(filename).__name__ == 'Key':
            filename = '/' + filename.name

        path = self._get_s3_path(filename)
        k = Key(bucket)
        k.key = path

        try:
            bucket.delete_key(k)
        except S3ResponseError:
            pass

    def delete(self, filename, storage_type=None, bucket_name=None):
        if not (storage_type and bucket_name):
            self._delete_local(filename)
        else:
            if storage_type != 's3':
                raise ValueError('Storage type "%s" is invalid, the only supported storage type (apart from default local storage) is s3.' % storage_type)

            self._delete_s3(filename, bucket_name)

    def _save_local(self, temp_file, filename, obj):
        path = self._get_path(filename)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission | 0o111)

        fd = open(path, 'wb')

        # Thanks to:
        # http://stackoverflow.com/a/3253276/2066849
        temp_file.seek(0)
        t = temp_file.read(1048576)
        while t:
            fd.write(t)
            t = temp_file.read(1048576)

        fd.close()

        if self.filesize_field:
            setattr(obj, self.filesize_field, os.path.getsize(path))

        return filename

    def _save_s3(self, temp_file, filename, obj):
        conn = S3Connection(self.access_key_id, self.access_key_secret)
        bucket = conn.get_bucket(self.bucket_name)

        path = self._get_s3_path(filename)
        k = bucket.new_key(path)
        k.set_contents_from_string(temp_file.getvalue())
        k.set_acl(self.acl)

        if self.filesize_field:
            setattr(obj, self.filesize_field, k.size)

        return filename

    def save(self, temp_file, filename, obj):
        if not (self.storage_type and self.bucket_name):
            ret = self._save_local(temp_file, filename, obj)
        else:
            if self.storage_type != 's3':
                raise ValueError('Storage type "%s" is invalid, the only supported storage type (apart from default local storage) is s3.' % self.storage_type)

            ret = self._save_s3(temp_file, filename, obj)

        if self.field_name:
            setattr(obj, self.field_name, ret)

        if self.storage_type == 's3':
            if self.storage_type_field:
                setattr(obj, self.storage_type_field, self.storage_type)
            if self.bucket_name_field:
                setattr(obj, self.bucket_name_field, self.bucket_name)
        else:
            if self.storage_type_field:
                setattr(obj, self.storage_type_field, '')
            if self.bucket_name_field:
                setattr(obj, self.bucket_name_field, '')

        return ret

    def _find_by_path_local(self, path):
        return glob('%s*' % path)

    def _find_by_path_s3(self, path, bucket_name):
        conn = S3Connection(self.access_key_id, self.access_key_secret)
        bucket = conn.get_bucket(bucket_name)

        s3_path = self._get_s3_path(path)

        return bucket.list(prefix=s3_path)

    def find_by_path(self, path, storage_type=None, bucket_name=None):
        if not (storage_type and bucket_name):
            return self._find_by_path_local(path)
        else:
            if storage_type != 's3':
                raise ValueError('Storage type "%s" is invalid, the only supported storage type (apart from default local storage) is s3.' % storage_type)

            return self._find_by_path_s3(path, bucket_name)
