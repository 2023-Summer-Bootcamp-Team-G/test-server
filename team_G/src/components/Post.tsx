// import React from "react";
import styled from "styled-components";

interface PostProps {
  parm: string;
  image: File | null;
}

function Post({ parm, image }: PostProps) {
  return (
    <PostContainer>
      <h3>{parm}</h3>
      {image && <Image src={URL.createObjectURL(image)} alt={parm} />}
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
