import styled from "styled-components";

interface PostProps {
  parm: string;
  image: File | string | null;
}

function Post({ parm, image }: PostProps) {
  let imageSource: string | null;

  if (image instanceof File) {
    imageSource = URL.createObjectURL(image);
  } else {
    imageSource = image;
  }

  return (
    <PostContainer>
      <h3>{parm}</h3>
      {imageSource && <Image src={imageSource} alt={parm} />}
    </PostContainer>
  );
}

export default Post;

const PostContainer = styled.div`
  border: 1px solid #ccc;
  padding: 16px;
  margin-bottom: 16px;
`;

const Image = styled.img`
  width: 200px;
  height: 200px;
  object-fit: cover;
  margin-bottom: 8px;
`;
